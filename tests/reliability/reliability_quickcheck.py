#!/usr/bin/env python3
"""Small local synthetic reliability exercise for AirOps 360.

This is NOT a Microsoft Fabric/Delta test. It deliberately uses a local
SQLite transaction to demonstrate the audit, rollback, and retry concepts
without reading or changing any Fabric data or external service.
"""
import argparse
import csv
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

BATCH_KEY = "synthetic_airline_month|2026|04"
BUSINESS_KEY = "SYN-FLT-0001"
SOURCE = {"flight_key": BUSINESS_KEY, "origin": "ORD", "destination": "ATL", "cancelled": 0}
SOURCE_BYTES = json.dumps(SOURCE, sort_keys=True, separators=(",", ":")).encode("utf-8")
SOURCE_HASH = hashlib.sha256(SOURCE_BYTES).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rows(db, sql, args=()):
    return [dict(r) for r in db.execute(sql, args).fetchall()]


def signature(db):
    recordset = rows(db, "SELECT batch_key, flight_key, origin, destination, cancelled FROM accepted ORDER BY flight_key")
    return hashlib.sha256(json.dumps(recordset, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def audit(db, *, run_id, load_id, attempt_no, status, before, after, error_class="", error_message=""):
    db.execute("""INSERT INTO audit
        (run_id, load_id, attempt_no, batch_key, source_hash, ingestion_status,
         source_row_count, target_row_count_before, target_row_count_after,
         reconciliation_status, error_class, error_message, completed_at_utc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, load_id, attempt_no, BATCH_KEY, SOURCE_HASH, status,
         1, before, after, "PASS" if status == "SUCCEEDED" else "FAIL",
         error_class, error_message, utc_now()))
    db.commit()


def run_attempt(db, attempt_no, *, inject_failure):
    run_id, load_id = str(uuid.uuid4()), str(uuid.uuid4())
    before = db.execute("SELECT COUNT(*) FROM accepted WHERE batch_key=?", (BATCH_KEY,)).fetchone()[0]
    try:
        db.execute("BEGIN IMMEDIATE")
        # Scope replacement by stable logical/business key, never blind append.
        db.execute("""INSERT INTO accepted
            (batch_key, flight_key, origin, destination, cancelled, source_hash, run_id, load_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(batch_key, flight_key) DO UPDATE SET
               origin=excluded.origin, destination=excluded.destination,
               cancelled=excluded.cancelled, source_hash=excluded.source_hash,
               run_id=excluded.run_id, load_id=excluded.load_id""",
            (BATCH_KEY, BUSINESS_KEY, SOURCE["origin"], SOURCE["destination"],
             SOURCE["cancelled"], SOURCE_HASH, run_id, load_id))
        if inject_failure:
            raise RuntimeError("CONTROLLED_SYNTHETIC_FAILURE_BEFORE_COMMIT")
        after = db.execute("SELECT COUNT(*) FROM accepted WHERE batch_key=?", (BATCH_KEY,)).fetchone()[0]
        if after != 1:
            raise AssertionError("Expected exactly one accepted synthetic flight")
        db.commit()
        audit(db, run_id=run_id, load_id=load_id, attempt_no=attempt_no,
              status="SUCCEEDED", before=before, after=after)
        return {"run_id": run_id, "load_id": load_id, "status": "SUCCEEDED"}
    except Exception as exc:
        db.rollback()
        after = db.execute("SELECT COUNT(*) FROM accepted WHERE batch_key=?", (BATCH_KEY,)).fetchone()[0]
        audit(db, run_id=run_id, load_id=load_id, attempt_no=attempt_no,
              status="FAILED", before=before, after=after,
              error_class=type(exc).__name__, error_message=str(exc))
        return {"run_id": run_id, "load_id": load_id, "status": "FAILED"}


def write_csv(path, records):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]) if records else ["none"])
        writer.writeheader()
        writer.writerows(records)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="evidence", help="Parent evidence directory")
    args = p.parse_args()
    parent = Path(args.out).resolve()
    parent.mkdir(parents=True, exist_ok=True)
    path = parent / ("run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    path.mkdir()
    db = sqlite3.connect(path / "synthetic.sqlite")
    db.row_factory = sqlite3.Row
    try:
        db.executescript("""
          CREATE TABLE accepted(
            batch_key TEXT NOT NULL, flight_key TEXT NOT NULL, origin TEXT,
            destination TEXT, cancelled INTEGER, source_hash TEXT NOT NULL,
            run_id TEXT NOT NULL, load_id TEXT NOT NULL,
            PRIMARY KEY(batch_key, flight_key));
          CREATE TABLE audit(
            run_id TEXT PRIMARY KEY, load_id TEXT NOT NULL, attempt_no INTEGER,
            batch_key TEXT NOT NULL, source_hash TEXT NOT NULL,
            ingestion_status TEXT NOT NULL, source_row_count INTEGER,
            target_row_count_before INTEGER, target_row_count_after INTEGER,
            reconciliation_status TEXT, error_class TEXT, error_message TEXT,
            completed_at_utc TEXT);
        """)
        db.execute("INSERT INTO accepted VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (BATCH_KEY, BUSINESS_KEY, SOURCE["origin"], SOURCE["destination"],
                    SOURCE["cancelled"], SOURCE_HASH, "fixture-baseline", "fixture-baseline"))
        db.commit()
        baseline = signature(db)
        failed = run_attempt(db, 1, inject_failure=True)
        after_failed = signature(db)
        after_failed_lineage = rows(db, "SELECT run_id FROM accepted")[0]["run_id"]
        recovered = run_attempt(db, 2, inject_failure=False)
        after_success = signature(db)
        accepted = rows(db, "SELECT * FROM accepted ORDER BY flight_key")
        audit_rows = rows(db, "SELECT * FROM audit ORDER BY attempt_no")
        checks = {
            "failed_attempt_recorded": failed["status"] == "FAILED" and audit_rows[0]["ingestion_status"] == "FAILED",
            "error_class_and_message_recorded": audit_rows[0]["error_class"] == "RuntimeError" and "CONTROLLED_SYNTHETIC_FAILURE" in audit_rows[0]["error_message"],
            "failure_did_not_modify_accepted_business_state": baseline == after_failed,
            "failure_rolled_back_attempt_lineage": after_failed_lineage == "fixture-baseline",
            "successful_retry_recorded": recovered["status"] == "SUCCEEDED" and audit_rows[1]["ingestion_status"] == "SUCCEEDED",
            "retry_kept_same_logical_batch": len({r["batch_key"] for r in audit_rows}) == 1,
            "retry_preserved_source_hash": len({r["source_hash"] for r in audit_rows}) == 1,
            "retry_created_fresh_run_and_load_ids": failed["run_id"] != recovered["run_id"] and failed["load_id"] != recovered["load_id"],
            "exactly_one_accepted_business_row": len(accepted) == 1 and accepted[0]["flight_key"] == BUSINESS_KEY,
            "accepted_business_state_idempotent": baseline == after_success,
            "successful_retry_updated_lineage_only": accepted[0]["run_id"] == recovered["run_id"],
            "audit_attempt_counts_reconcile": len(audit_rows) == 2 and all(r["target_row_count_before"] == 1 and r["target_row_count_after"] == 1 for r in audit_rows),
        }
        write_csv(path / "audit.csv", audit_rows)
        write_csv(path / "accepted_business_state.csv", accepted)
        report = {
            "scope": "LOCAL SYNTHETIC SQLITE TRANSACTION ONLY; NOT FABRIC OR PRODUCTION",
            "batch_key": BATCH_KEY, "source_hash": SOURCE_HASH,
            "baseline_business_sha256": baseline, "after_failure_business_sha256": after_failed,
            "after_retry_business_sha256": after_success,
            "failed_run_id": failed["run_id"], "retry_run_id": recovered["run_id"],
            "accepted_row_count": len(accepted), "checks": checks,
            "overall": "PASS" if all(checks.values()) else "FAIL",
        }
        (path / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        line_checks = "\n".join("- " + ("PASS" if v else "FAIL") + ": " + k.replace("_", " ") for k,v in checks.items())
        summary = (f"# AirOps 360 - Local Synthetic Failure and Retry Evidence\n\n"
                   f"**Result:** {report['overall']} ({sum(checks.values())}/{len(checks)} checks)\n\n"
                   f"**Scope:** Local SQLite synthetic transaction, not a Fabric, Spark, Delta, or production test.\n\n"
                   f"**Fixture:** one artificial flight, `batch_key={BATCH_KEY}`, original accepted row count 1.\n\n"
                   f"**Attempt 1:** new run `{failed['run_id']}`. Raised controlled failure after staged UPSERT, before commit. Transaction rolled back. Audit status FAILED, error retained. Accepted business state and lineage unchanged.\n\n"
                   f"**Attempt 2:** new run `{recovered['run_id']}` for same batch/source. Commit succeeded. Audit status SUCCEEDED, exactly one accepted flight remains. Only execution metadata changed.\n\n"
                   f"**Evidence files:** `audit.csv`, `accepted_business_state.csv`, `validation.json`.\n\n"
                   f"## Automated checks\n\n{line_checks}\n\n"
                   f"## Production boundary\n\nThis exercise does not establish that the existing Fabric BTS delete-then-append path is atomic or safe during a write failure. Do not inject a failure into the real April dataset. Actual Fabric failure recovery needs its own isolated Delta integration test.\n")
        (path / "EVIDENCE.md").write_text(summary, encoding="utf-8")
        print(f"{report['overall']}: {sum(checks.values())}/{len(checks)} local synthetic checks")
        print(f"FAILED run_id={failed['run_id']}")
        print(f"SUCCEEDED run_id={recovered['run_id']}")
        print("Accepted business rows:", len(accepted))
        print("Evidence:", path)
        return 0 if all(checks.values()) else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
