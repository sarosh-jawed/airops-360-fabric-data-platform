# AirOps 360 - Five tasks, one quick reliability exercise

## Purpose and boundary

Complete a short, safe synthetic failure/recovery learning artifact supporting Week 7 tasks W7-12, W7-19, W7-20, W7-23, and W7-27. The repository already has validated April BTS Bronze rerun evidence, Silver business-key checks, and Gold KPI reconciliation. Do not repeat those runs.

**Important:** This harness uses a local SQLite transaction with AirOps' existing `batch_key`, `run_id`, `load_id`, `FAILED`/`SUCCEEDED`, and error-field concepts. It does **not** execute the Fabric notebook or prove atomic recovery for the production Delta path. There is no external API, network call, Fabric credential, production-table access, or dependency beyond Python 3.9+ standard library.

The current Bronze operations runbook already describes these concepts in `docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md`. The original BTS notebook uses delete then append, so do not fault-inject its real April Bronze table.

## Run (Windows PowerShell)

From this extracted folder:

```powershell
py -3 .\reliability_quickcheck.py --out .\evidence
if ($LASTEXITCODE -ne 0) { throw 'Synthetic reliability quickcheck failed' }
```

Expected console outcome: `PASS: 12/12 local synthetic checks`, FAILED audit followed by SUCCEEDED audit with different run IDs, and `Accepted business rows: 1`. The program creates a **new subfolder for each run** with `EVIDENCE.md`, `validation.json`, `audit.csv`, `accepted_business_state.csv`, and a separate `synthetic.sqlite` test database. No existing evidence is overwritten.

## W7-12 + W7-20: What this proves

The artificial fixture starts with one accepted flight. Attempt 1 stages an UPSERT and triggers a controlled exception before commit. SQLite rolls back. The audit records `FAILED`, exception type/reason, source/target counts, and IDs. Attempt 2 uses the same logical batch/source hash but new run/load IDs, succeeds and retains exactly one accepted business row. A hash of business columns stays constant before failure, after failure and after retry. The accepted row's execution lineage changes only on successful retry.

**Limit:** This demonstrates transaction and audit reasoning locally. It does not demonstrate the actual Fabric write's failure safety. Do not call it a live pipeline recovery test.

## W7-19: Reproducibility handoff

- **Prerequisite:** Python 3.9 or later and this extracted folder. Windows `py -3` launcher; on macOS/Linux use `python3`.
- **Input:** One synthetic ORD to ATL flight, deterministic payload and SHA-256, stable `synthetic_airline_month|2026|04` logical batch.
- **Command:** `py -3 .\reliability_quickcheck.py --out .\evidence`.
- **Expected output:** 12/12 PASS, failure audit + retry audit, 1 accepted business row, unchanged business signature.
- **Recovery if check fails:** Inspect `validation.json` and `audit.csv`; fix the local test, rerun to a fresh evidence directory. Do not touch a live Fabric table.
- **Environment boundary:** Local SQLite here; Fabric notebooks live in the Fabric workspace; Docker validation for DotNetScope is a different application. This quickcheck is not a substitute for a Fabric/Spark/Delta end-to-end test.

## W7-23: Three evidence-based design gates

1. **Incremental loads:** Add them when there is a new-month/daily data-arrival SLA, volume or rerun-cost measurement making full batch replacement unacceptable, and a tested watermark/late-arrival policy. No evidence here requires incremental ingestion yet.
2. **Expand weather:** Extend beyond ORD/ATL only after an analytical question or stakeholder requires other airports, with demonstrated coverage rates, API limits, timezone handling, null semantics and backfill budget. April pilot-only null weather is unknown, not good weather.
3. **Public hosting:** Add it when recruiters/users demonstrably need a live, repeatable shared demo, and a hosting/security/cost plan exists. Existing screenshots, docs and local reproduction may suffice until then.

## W7-27: Interview story (90 seconds, read aloud)

**Problem (~30 s):** "I built AirOps 360 to make flight performance data trustworthy across ingestion, transformations and BI. One risk with batch pipelines is that a retry can accidentally duplicate a flight or leave inconsistent data after failure."

**Action (~40 s):** "For the April BTS batch, I had previously validated idempotent ingestion: 597,919 logical flights after an unchanged rerun and no duplicate business-key groups. Separately, I created a one-flight local synthetic failure experiment. I forced a failure after staging an update but before committing, kept an audit row with the failure reason, then retried the same logical batch with new run identifiers."

**Evidence and boundary (~20 s):** "The local test recorded FAILED then SUCCEEDED, preserved one business row and unchanged business fields, and passed all automated checks. This is a SQLite-based teaching proof, not evidence that my Fabric Delta job is transactionally safe under injected faults. I'd validate that separately in an isolated Fabric table before claiming production recovery."

## Next action

Keep the quickcheck outside your repository unless you decide its truthful local-demo scope adds value. If you commit it later, put the script in `tests/reliability/` and this guide in `docs/reliability/`, using a feature branch and a PR. Do not upload generated databases or run-specific audit IDs unless needed; `.gitignore` the evidence folder if moving it into the repo.
