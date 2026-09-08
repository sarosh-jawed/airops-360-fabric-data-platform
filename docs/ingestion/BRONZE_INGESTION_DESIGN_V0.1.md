# AirOps 360 Bronze Ingestion Design v0.1

**Status:** Implementation-ready design  
**Version:** 0.1  
**Date:** 2026-09-08  
**Target Lakehouse:** `lh_airops_bronze`  
**Architecture:** `docs/ARCHITECTURE.md`  
**Data contract:** `docs/DATA_CONTRACT.md`  
**Evidence basis:** `docs/profiling/BTS_2026_04_PROFILE.md`, `config/airports_v0.1.csv`  
**Related implementation work:** GitHub Issues #4, #5, and #8

---

## 1. Purpose

This document defines the Week 3 implementation contract for AirOps 360 Bronze ingestion.

It converts the accepted architecture and source data contract into concrete conventions for:

- raw and Bronze storage paths
- object and table naming
- source and ingestion metadata
- `run_id`, `load_id`, and deterministic batch identity
- pipeline/notebook parameters
- source-to-Bronze reconciliation
- idempotent reruns
- failure and retry behavior

The scope is intentionally limited to Bronze ingestion. Silver transformations, Gold implementation, Direct Lake, and production CI/CD implementation are outside this design.

---

## 2. Design principles

1. Bronze preserves source truth. No business-rule transformation, deduplication, or enrichment is performed in Bronze.
2. Every successful source batch is reproducible and traceable to its source object, parameters, contract version, run, and load attempt.
3. Raw source artifacts are preserved separately from the Bronze Delta representation.
4. Batch identity is deterministic; execution identity is not.
5. A rerun of the same logical batch must not multiply Bronze records.
6. Operational history is preserved in an append-only audit table even when the current Bronze batch is replaced idempotently.
7. Contract or schema failures fail safely and are never converted into a successful load.
8. Delta publication is atomic at the logical batch level so a failed attempt does not leave a partially published successful batch.

---

## 3. Bronze objects and naming conventions

### 3.1 Fabric Lakehouse

```text
lh_airops_bronze
```

### 3.2 Orchestration and notebooks

Primary orchestration item already defined by Architecture v0.1:

```text
pl_monthly_airops
```

Week 3 Bronze notebook naming:

```text
nb_bronze_ingest_bts
nb_bronze_ingest_weather
```

These names keep orchestration separate from ingestion logic while remaining small enough for the MVP.

### 3.3 Bronze Delta tables

```text
brz_bts_flights
brz_weather_api_raw
brz_ingestion_audit
```

Grains:

| Table | Grain |
|---|---|
| `brz_bts_flights` | one source BTS row plus Bronze lineage columns |
| `brz_weather_api_raw` | one Open-Meteo airport/month response plus request/response lineage |
| `brz_ingestion_audit` | one source-object load attempt |

`brz_weather_api_raw` stores the raw API response as a source-preserving payload. Hourly weather normalization belongs in Silver and is not a Bronze responsibility.

---

## 4. Raw storage paths

### 4.1 BTS flight source

Raw landing path:

```text
Files/raw/flights/year=YYYY/month=MM/
```

Normalized source filename:

```text
bts_reporting_carrier_ontime_YYYY_MM.csv
```

April 2026 example:

```text
Files/raw/flights/year=2026/month=04/bts_reporting_carrier_ontime_2026_04.csv
```

If the provider source is delivered as an archive, preserve the provider archive when practical and record both the archive name and extracted source object in audit metadata.

### 4.2 Open-Meteo source

Raw response path:

```text
Files/raw/weather/airport=<AIRPORT>/year=YYYY/month=MM/
```

Raw response filename:

```text
open_meteo_<AIRPORT>_YYYY_MM.json
```

Example:

```text
Files/raw/weather/airport=ORD/year=2026/month=04/open_meteo_ORD_2026_04.json
```

One raw JSON object should correspond to one airport/month request whenever practical.

### 4.3 Controlled airport reference

Version-controlled source of truth:

```text
config/airports_v0.1.csv
```

Fabric working copy, when needed by the weather notebook:

```text
Files/reference/airports/airports_v0.1.csv
```

The GitHub version remains the governed configuration artifact. The Fabric copy must match the committed version used by the run.

---

## 5. Identity model: batch, run, and load

AirOps uses three separate identifiers because they answer different operational questions.

### 5.1 `batch_key`: What logical source batch is this?

`batch_key` is deterministic and stable across reruns.

BTS:

```text
bts_reporting_carrier_ontime|YYYY|MM
```

April example:

```text
bts_reporting_carrier_ontime|2026|04
```

Open-Meteo:

```text
open_meteo_historical_weather|AIRPORT|YYYY|MM|variable_set_version
```

Example:

```text
open_meteo_historical_weather|ORD|2026|04|wx_v1
```

### 5.2 `run_id`: Which end-to-end pipeline execution is this?

`run_id` is a unique UUID generated once at the beginning of `pl_monthly_airops` and propagated to all activities executed by that pipeline run.

Recommended representation:

```text
UUID
```

Example shape:

```text
7f2f2fd4-5c3c-4c70-b4c6-5a04a87b65ab
```

A new manual rerun or scheduled rerun receives a new `run_id`.

### 5.3 `load_id`: Which source load attempt is this?

`load_id` is a unique UUID for one source-object load attempt inside a pipeline run.

Examples:

- one BTS April load in a run = one `load_id`
- one ORD April Open-Meteo request/load = one `load_id`
- one ATL April Open-Meteo request/load = a different `load_id`

Automatic retry of the same activity retains the same `load_id` and increments `attempt_no`.

A new pipeline rerun generates a new `run_id` and new `load_id`, while the deterministic `batch_key` remains unchanged.

This separation allows AirOps to prove both execution lineage and idempotency.

---

## 6. Pipeline and notebook parameters

### 6.1 Parent pipeline parameters

`pl_monthly_airops` uses the following minimum parameters for Bronze execution:

| Parameter | Example | Required | Purpose |
|---|---|---:|---|
| `p_year` | `2026` | Yes | logical load year |
| `p_month` | `04` | Yes | logical load month |
| `p_load_mode` | `historical` | Yes | `historical` or `incremental` |
| `p_run_id` | generated UUID | Yes | end-to-end run lineage |
| `p_contract_version` | `0.1` | Yes | governing contract version |

### 6.2 BTS ingestion parameters

`nb_bronze_ingest_bts` receives:

| Parameter | Required | Derivation |
|---|---:|---|
| `p_year` | Yes | parent pipeline |
| `p_month` | Yes | parent pipeline |
| `p_run_id` | Yes | parent pipeline |
| `p_load_id` | Yes | generated for BTS load |
| `p_contract_version` | Yes | parent pipeline |
| `p_source_name` | Yes | `bts_reporting_carrier_ontime` |
| `p_source_file_name` | Yes | deterministic filename |
| `p_source_uri` | When available | provider or landing URI |
| `p_batch_key` | Yes | deterministic BTS batch key |

### 6.3 Weather ingestion parameters

`nb_bronze_ingest_weather` receives:

| Parameter | Required | Purpose |
|---|---:|---|
| `p_year` | Yes | load year |
| `p_month` | Yes | load month |
| `p_run_id` | Yes | end-to-end lineage |
| `p_load_id` | Yes | airport/month load identity |
| `p_contract_version` | Yes | governing contract |
| `p_airport_code` | Yes | configured active airport |
| `p_latitude` | Yes | controlled airport reference |
| `p_longitude` | Yes | controlled airport reference |
| `p_timezone` | Yes | airport IANA timezone |
| `p_variable_set_version` | Yes | initially `wx_v1` |
| `p_start_date` | Yes | request boundary |
| `p_end_date` | Yes | request boundary |
| `p_batch_key` | Yes | deterministic weather batch key |

The non-secret request parameters are persisted in `parameters_json` so the request can be reproduced later.

---

## 7. Bronze row-level lineage

`brz_bts_flights` preserves all 110 source columns from the April BTS extract and adds only technical lineage columns.

Required Bronze lineage columns:

```text
_bronze_run_id
_bronze_load_id
_bronze_batch_key
_bronze_contract_version
_bronze_source_name
_bronze_source_file_name
_bronze_source_hash
_bronze_ingested_at_utc
_bronze_load_year
_bronze_load_month
```

Rules:

- Source columns retain their original source names in Bronze.
- Bronze does not rename source fields to analytical naming standards.
- Bronze does not generate final Silver/Gold business attributes.
- The April source schema baseline is 110 source columns. Bronze therefore contains those 110 source columns plus the technical lineage columns above.
- Source values are preserved without business-rule rewriting.
- Explicit typing, time normalization, key derivation, and domain cleanup occur in Silver.

For `brz_weather_api_raw`, preserve:

```text
response_json
airport_code
request_start_date
request_end_date
response_timezone
response_utc_offset_seconds
_bronze_run_id
_bronze_load_id
_bronze_batch_key
_bronze_contract_version
_bronze_source_name
_bronze_ingested_at_utc
```

---

## 8. Ingestion audit table

### 8.1 Table

```text
brz_ingestion_audit
```

### 8.2 Grain

```text
one source-object load attempt
```

### 8.3 Required fields

| Field | Purpose |
|---|---|
| `run_id` | end-to-end pipeline execution |
| `load_id` | source load identity |
| `attempt_no` | retry attempt number |
| `batch_key` | deterministic logical batch |
| `contract_version` | governing data contract |
| `source_name` | stable source identifier |
| `source_object` | source file or API request identity |
| `source_uri` | provider/landing URI when available |
| `source_file_name` | original/normalized filename for file loads |
| `source_hash` | checksum when feasible |
| `load_year` | logical load year |
| `load_month` | logical load month |
| `airport_code` | weather source only; otherwise NULL |
| `variable_set_version` | weather source only; otherwise NULL |
| `pipeline_name` | executing pipeline |
| `activity_name` | notebook/activity |
| `load_mode` | historical or incremental |
| `started_at_utc` | attempt start |
| `completed_at_utc` | terminal timestamp |
| `ingestion_status` | `STARTED`, `SUCCEEDED`, or `FAILED` |
| `source_row_count` | source records or observations when measurable |
| `source_column_count` | source column count when applicable |
| `processed_row_count` | records processed by ingestion activity |
| `target_row_count_before` | target batch rows before publication |
| `target_row_count_after` | target batch rows after publication |
| `rejected_row_count` | later-stage use; normally 0/NULL in source-preserving Bronze |
| `reconciliation_status` | `PASS`, `FAIL`, or `NOT_RUN` |
| `parameters_json` | reproducible non-secret parameters |
| `error_class` | failure category |
| `error_message` | diagnostic failure message |

Audit rows are append-only operational evidence. A rerun never deletes earlier audit history.

---

## 9. April BTS reconciliation contract

The verified April 2026 source baseline is:

```text
source rows:    597,919
source columns: 110
required AirOps fields present: 20 / 20
candidate business-key uniqueness: 100% for April
```

The Week 3 Bronze load passes reconciliation only if:

1. the source is readable;
2. the source has 597,919 rows for the verified April artifact;
3. the source exposes 110 source columns;
4. all 20 required contract fields remain present;
5. `brz_bts_flights` contains exactly 597,919 rows for the April `batch_key` after publication;
6. every April Bronze row has non-null `run_id`, `load_id`, `batch_key`, `contract_version`, source name, and ingestion timestamp lineage;
7. source count minus Bronze batch count equals zero;
8. the audit row reaches `SUCCEEDED` only after all checks above pass.

Recommended calculated evidence:

```text
row_count_difference = target_row_count_after - source_row_count
```

Expected Week 3 result:

```text
row_count_difference = 0
reconciliation_status = PASS
```

The April business-key uniqueness profile is retained as source evidence, but business-key generation/deduplication remains a Silver responsibility.

---

## 10. Idempotent rerun strategy

### 10.1 Principle

The same deterministic `batch_key` may be executed multiple times, but `brz_bts_flights` must contain only one current published copy of that logical batch.

### 10.2 Controlled batch replacement

For the Bronze Delta representation, publication uses controlled replacement of the target batch rather than unconditional append.

Conceptually:

```text
identify deterministic batch_key
    -> read and validate complete source
    -> calculate source count/hash/schema evidence
    -> atomically replace only that batch in Bronze Delta
    -> reconcile published batch count
    -> mark audit attempt SUCCEEDED
```

A new pipeline rerun therefore produces:

- a new `run_id`
- a new `load_id`
- the same `batch_key`
- a new append-only audit record
- the same logical Bronze batch population when the source is unchanged

For April, the idempotency proof should show:

```text
first successful batch row count  = 597,919
rerun successful batch row count  = 597,919
unintended duplicate increase     = 0
```

### 10.3 Source mutation guard

If a raw object already exists for the same deterministic `batch_key` but its `source_hash` differs from the previously successful source hash, the pipeline must not silently treat it as an ordinary rerun.

Expected behavior:

```text
FAIL / REQUIRE EXPLICIT REVIEW
```

This protects reproducibility if a provider republishes a changed file under the same logical month.

---

## 11. Failure and retry expectations

### 11.1 Fail before target mutation

The following failures occur before replacing the successful Bronze Delta batch:

- invalid year/month or unsupported load mode
- source file missing or unreadable
- required source columns missing
- source hash calculation failure when the hash is required
- source batch identity mismatch
- weather airport missing from active controlled configuration
- unrecoverable API response/schema failure

A failed attempt records audit evidence as `FAILED` and preserves the last successful Bronze batch.

### 11.2 Retryable failures

Retry only transient failures.

BTS/file ingestion:

```text
automatic retries: 1
use for: transient storage/network/Spark execution failure
```

Open-Meteo:

```text
automatic retries: up to 3
use for: timeout, HTTP 429, and retryable 5xx responses
strategy: exponential backoff with jitter
```

### 11.3 Non-retryable failures

Do not automatically retry:

- invalid parameters
- missing required columns
- contract-version mismatch
- malformed required source structure
- deterministic batch-key mismatch
- changed source hash for an already successful logical batch without explicit review
- invalid airport configuration

These failures require correction or an explicit decision before another run.

### 11.4 Audit status transitions

Normal success:

```text
STARTED -> SUCCEEDED
```

Terminal failure:

```text
STARTED -> FAILED
```

Automatic retries retain the same `load_id` and increment `attempt_no`; final status reflects the terminal result.

---

## 12. Week 3 implementation sequence

This design supports the approved Week 3 order without expanding scope.

### Wednesday

Create/verify:

```text
lh_airops_bronze
Files/raw/flights/
Files/raw/weather/
Files/reference/airports/
brz_bts_flights
brz_weather_api_raw
brz_ingestion_audit
```

Only create items required for Bronze execution.

### Thursday

Implement and run April BTS ingestion:

```text
batch_key = bts_reporting_carrier_ontime|2026|04
expected source rows = 597,919
expected source columns = 110
```

### Friday

Run reconciliation and the same April load again. Capture before/after counts, `run_id`, `load_id`, and `batch_key` to prove idempotency.

### Saturday

Run a small Open-Meteo API-to-Bronze pilot using active airports from `config/airports_v0.1.csv`.

This remains a pilot, not a complete historical backfill.

### Sunday

Publish only verified screenshots, run evidence, and documentation that match the actual implemented state.

---

## 13. Week 3 Bronze evidence checklist

Task 1 design evidence:

- [x] raw/Bronze paths defined
- [x] naming conventions defined
- [x] source metadata defined
- [x] batch metadata defined
- [x] `run_id` defined
- [x] `load_id` defined
- [x] deterministic `batch_key` defined
- [x] pipeline/notebook parameters defined
- [x] reconciliation fields and pass criteria defined
- [x] idempotent rerun behavior defined
- [x] failure behavior defined
- [x] retry behavior defined
- [x] April source baseline mapped into the design
- [x] Open-Meteo pilot path mapped without expanding scope

Implementation evidence remains pending and belongs to the Wednesday-Saturday Week 3 tasks.

---

## 14. Definition of Done for Bronze design v0.1

Bronze ingestion design v0.1 is complete when an engineer can implement the April BTS Bronze load and scoped weather pilot without inventing new conventions for storage, identity, lineage, parameters, reconciliation, or failure handling.

This document satisfies that design requirement while keeping actual Fabric creation and ingestion execution in their scheduled Week 3 tasks.
