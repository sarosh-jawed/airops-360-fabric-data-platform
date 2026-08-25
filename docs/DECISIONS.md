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

