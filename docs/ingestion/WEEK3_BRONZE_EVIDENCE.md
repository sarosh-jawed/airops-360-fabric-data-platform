# AirOps 360 — Week 3 Bronze Evidence

**Checkpoint:** Week 3 Bronze implementation  
**Platform:** Microsoft Fabric  
**Workspace:** `AirOps 360`  
**Bronze Lakehouse:** `lh_airops_bronze`  
**Status:** PASS for the scoped Week 3 implementation

---

## 1. Purpose

This document records the run evidence for the AirOps 360 Week 3 Bronze implementation.

It is intentionally limited to work that was actually executed and validated:

- April 2026 BTS Bronze ingestion
- source-to-Bronze reconciliation
- idempotent BTS rerun
- scoped Open-Meteo Bronze pilot for ORD and ATL
- Bronze ingestion metadata and audit behavior

This checkpoint does **not** claim Silver, Gold physical tables, Direct Lake, or Power BI implementation.

---

## 2. Fabric objects used

### Workspace

```text
AirOps 360
```

### Lakehouse

```text
lh_airops_bronze
```

### Fabric notebooks executed

```text
nb_bronze_environment_setup
nb_bronze_ingest_bts
nb_bronze_ingest_weather
```

### Bronze tables

```text
brz_bts_flights
brz_weather_api_raw
brz_ingestion_audit
```

---

## 3. April 2026 BTS source profile

Source:

```text
BTS Reporting Carrier On-Time Performance
April 2026
```

Validated profile:

| Check | Result |
|---|---:|
| Source rows | 597,919 |
| Source columns | 110 |
| Required AirOps fields present | 20 / 20 |
| `FlightDate` parse failures | 0 |
| Rows outside April 2026 | 0 |
| Candidate-key null rows | 0 |
| Duplicate candidate-key groups | 0 |

Provisional flight business key:

```text
FlightDate
+ Reporting_Airline
+ Flight_Number_Reporting_Airline
+ Origin
+ Dest
+ CRSDepTime
```

The key was 100% unique for the April source batch. Future batches must continue to validate it rather than assuming permanent uniqueness.

---

## 4. Initial BTS Bronze load

### Logical batch

```text
bts_reporting_carrier_ontime|2026|04
```

### Execution evidence

```text
run_id:
d45b7c25-d751-4104-9476-e94a1c75fcbd

load_id:
a5e5c360-d0e5-4bbe-9e7e-6991a5331bac

source_sha256:
71b1ac148bb7a344161b5eeb846aa662fae8d986b37025f8d8d92383b8c13ee7
```

### Reconciliation

| Check | Result |
|---|---:|
| Source rows | 597,919 |
| Bronze rows | 597,919 |
| Source columns | 110 |
| Bronze columns | 120 |
| Added ingestion/lineage columns | 10 |
| Required source-schema match | PASS |
| Required metadata null count | 0 |
| Row-count reconciliation | PASS |

Result:

```text
TASK 14 STATUS: PASS
```

---

## 5. BTS idempotent rerun

The same logical April batch was executed again without changing the source data.

### Before rerun

```text
rows = 597,919
```

### Rerun execution

```text
run_id:
53b674ff-4ee3-4edb-9c81-c44fb1554a79

load_id:
0570a579-1191-4c84-9721-b0882005baae
```

### After rerun

| Check | Result |
|---|---:|
| Rows before | 597,919 |
| Rows after | 597,919 |
| Source SHA-256 | unchanged |
| Duplicate business-key groups | 0 |
| Logical business state | unchanged |
| `run_id` | changed |
| `load_id` | changed |
| Idempotency result | PASS |

### Interpretation

The rerun is idempotent because the same logical input produced the same logical business state.

`run_id` and `load_id` are allowed to change because they describe a new execution and load attempt. Idempotency does **not** require execution metadata to remain identical.

---

## 6. Open-Meteo Bronze pilot

### Scope

Airports:

```text
ORD
ATL
```

Period:

```text
2026-04-01 through 2026-04-30
```

Variable-set version:

```text
wx_v1
```

### Expected source behavior

April 2026 contains 30 days:

```text
30 × 24 = 720 hourly observations per airport
```

### Observed evidence

| Airport | IANA timezone | Hourly observations | Attempt | Result |
|---|---|---:|---:|---|
| ORD | `America/Chicago` | 720 | 1 | PASS |
| ATL | `America/New_York` | 720 | 1 | PASS |

Hash evidence:

```text
ORD SHA-256 prefix: c75a37281aae...
ATL SHA-256 prefix: 8842f586979f...
```

Landing/reconciliation results:

| Check | Result |
|---|---:|
| Airports requested | 2 |
| Raw JSON files landed | 2 |
| Bronze response rows | 2 |
| Deterministic batch keys | 2 |
| Shared pipeline `run_id` count | 1 |
| Distinct `load_id` count | 2 |
| Required metadata nulls | 0 |
| Extraction validation | PASS |
| Bronze MERGE | PASS |
| Audit append | PASS |

Result:

```text
TASK 26 STATUS: PASS
```

---

## 7. Why the weather Bronze grain is one airport/month response

The Open-Meteo Bronze layer preserves the source response rather than prematurely transforming it into analytical rows.

Bronze grain:

```text
one Open-Meteo airport/month API response
```

The raw JSON is retained with request and response lineage.

Hourly normalization is intentionally deferred to Silver, where the analytical weather grain becomes:

```text
one airport + one local observation hour
```

This separation keeps Bronze reproducible and source-faithful while allowing Silver to own schema standardization.

---

## 8. Bronze identity model

AirOps uses different identifiers for different purposes.

### `batch_key`

Stable logical identity of a source batch.

Example:

```text
bts_reporting_carrier_ontime|2026|04
```

A rerun of the same logical April data keeps the same `batch_key`.

### `run_id`

Identity of one end-to-end pipeline execution.

A rerun receives a new `run_id`.

### `load_id`

Identity of one source-object load attempt.

Multiple source objects within the same run can have different `load_id` values.

### Future `flight_key`

The deterministic identity of one logical flight record. It belongs to standardized downstream processing rather than the raw source-response identity model.

---

## 9. Reliability controls demonstrated

The Week 3 Bronze implementation demonstrated:

- deterministic logical batches
- source hashing
- ingestion lineage
- source-to-target row reconciliation
- metadata-null validation
- duplicate business-key validation
- controlled rerun behavior
- idempotent BTS replacement/MERGE behavior
- preserved raw weather JSON
- bounded retry design for transient API failures
- audit status progression
- separation of business state from execution metadata

---

## 10. Screenshot status

No Fabric screenshots are included in this Week 3 evidence checkpoint.

The checkpoint is based on executed run output and reconciliation evidence recorded during implementation. Screenshots can be added later during portfolio-release polishing without changing the underlying technical claims.

---

## 11. Claims intentionally excluded

This evidence pack does **not** claim completion of:

- Silver flight transformations
- hourly Silver weather normalization
- flight/weather enrichment
- physical Gold tables
- Gold incremental publication
- Direct Lake
- Power BI
- Fabric deployment pipelines
- production-scale multi-month weather backfill

Those items remain future implementation work.

---

## 12. Week 3 Bronze conclusion

The scoped Bronze objective is complete:

```text
BTS April ingestion            PASS
BTS reconciliation             PASS
BTS idempotent rerun           PASS
ORD weather pilot              PASS
ATL weather pilot              PASS
raw JSON preservation          PASS
Bronze metadata validation     PASS
audit behavior                 PASS
```

The project can now move into Silver standardization and quality processing without overstating downstream implementation.
