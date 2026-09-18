# Week 4 Fabric Continuity Checkpoint

Date checked: 2026-09-17

## Capacity status

The AirOps 360 Fabric workspace displayed:
"Your free Microsoft Fabric trial ends in 8 days."

Based on the Sep 17 checkpoint, the capacity is expected to expire around
Sep 25, 2026. The exact capacity expiration timestamp is not exposed under
the university-provided student account permissions.

A separate Power BI Pro trial displayed 38 days remaining. This is separate
from the Fabric-capacity deadline used for AirOps continuity planning.

## Backup scope

Critical Fabric notebooks were exported as .ipynb and version-controlled:

Bronze:
- nb_bronze_environment_setup
- nb_bronze_ingest_bts
- nb_bronze_ingest_weather

Silver:
- nb_silver_standardize_flights
- nb_silver_flight_key_dq_gate
- nb_interview_pyspark_silver_exercises

Production BTS/Delta datasets are intentionally excluded from Git.

## Continuity decision

Because fewer than 14 days remain on the Fabric capacity, Week 5 should
prioritize a minimal end-to-end Gold-to-Power-BI vertical slice after the
validated Silver layer. The goal is to preserve portfolio evidence of the
complete Bronze -> Silver -> Gold -> Power BI architecture before capacity
expiration.
