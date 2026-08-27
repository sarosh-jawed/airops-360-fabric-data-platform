\# Architecture Decision Log



This file records material decisions that affect AirOps 360 scope or architecture.



\---



\## ADR-001 — Microsoft Fabric as primary platform



Status: Accepted



Decision:

Use Microsoft Fabric as the primary analytics and data engineering platform.



Reason:

The project is intended to demonstrate practical Fabric Data Engineering skills including OneLake, Lakehouse, Spark, Delta Lake, pipelines, Direct Lake, and Power BI.



\---



\## ADR-002 — Medallion architecture



Status: Accepted



Decision:

Use Bronze, Silver, and Gold layers.



Reason:

The pattern creates explicit boundaries between raw, validated, and analytics-ready data and aligns with Microsoft Fabric guidance.



\---



\## ADR-003 — Batch rather than streaming



Status: Accepted



Decision:

Implement monthly batch ingestion.



Reason:

BTS flight data is published in batches, and batch processing allows the project to demonstrate ingestion, incremental loading, reconciliation, and idempotency without introducing unnecessary streaming complexity.



\---



\## ADR-004 — Limit weather enrichment



Status: Accepted



Decision:

Weather enrichment will initially cover approximately 15 high-volume airports.



Reason:

This provides sufficient analytical value while keeping API usage, processing cost, and development complexity manageable.
---

## ADR-005 - Deterministic incremental loading and idempotent reruns

Status: Accepted

Decision:

Treat year and month as the BTS incremental boundary, use deterministic source batch keys, derive a deterministic flight key in Silver, and use merge/upsert behavior in Gold so rerunning an unchanged batch does not create duplicate business records.

Reason:

The portfolio must demonstrate production-style incremental loading, traceability, reconciliation, and safe reruns rather than simple append-only notebook processing.

---

## ADR-006 - Data contracts govern ingestion and transformation behavior

Status: Accepted

Decision:

Use `docs/DATA_CONTRACT.md` as the governing contract for required source fields, source grain, batch identity, key semantics, lineage metadata, time-zone handling, schema evolution, and validation behavior.

Reason:

Making the contract an explicit architecture input prevents silent schema drift and keeps ingestion, quality checks, and downstream models reproducible.

---

## ADR-007 - Airport-local time is the canonical weather-alignment context

Status: Accepted

Decision:

Preserve BTS schedule values as local source time and align weather observations using the origin airport's controlled IANA time zone and scheduled departure hour.

Reason:

BTS schedule fields are local-time values. Explicit airport-local alignment avoids incorrect UTC assumptions and makes flight-weather enrichment reproducible.