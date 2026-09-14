# AirOps 360 — Bronze Operations Runbook

**Scope:** Current Week 3 Bronze implementation  
**Platform:** Microsoft Fabric  
**Workspace:** `AirOps 360`  
**Lakehouse:** `lh_airops_bronze`

---

## 1. Purpose

This runbook defines the repeatable operating procedure for the currently implemented AirOps 360 Bronze layer.

It covers:

- April BTS file ingestion
- scoped Open-Meteo ingestion
- reconciliation
- idempotent reruns
- audit checks
- failure/retry behavior

It does not describe Silver or Gold execution because those layers are not yet implemented.

---

## 2. Current Fabric notebooks

```text
nb_bronze_environment_setup
nb_bronze_ingest_bts
nb_bronze_ingest_weather
```

The notebook names above refer to the Fabric workspace implementation.

---

## 3. Current Bronze tables

```text
brz_bts_flights
brz_weather_api_raw
brz_ingestion_audit
```

---

## 4. Storage conventions

### BTS raw files

```text
Files/raw/flights/year=YYYY/month=MM/bts_reporting_carrier_ontime_YYYY_MM.csv
```

### Weather raw files

```text
Files/raw/weather/airport=<AIRPORT>/year=YYYY/month=MM/open_meteo_<AIRPORT>_YYYY_MM.json
```

### Airport reference

```text
Files/reference/airports/airports_v0.1.csv
```

---

## 5. Preflight checklist

Before running a Bronze ingestion:

- [ ] Confirm the notebook is attached to `lh_airops_bronze`.
- [ ] Confirm the expected raw/reference path exists.
- [ ] Confirm the logical year/month parameters.
- [ ] Confirm the expected `batch_key`.
- [ ] Confirm the data-contract version used by the notebook.
- [ ] For BTS, verify required source fields are present.
- [ ] For weather, verify airport configuration contains code, coordinates, and IANA timezone.
- [ ] Do not proceed with a source mutation silently; compare source hash when rerunning an existing logical batch.

---

## 6. BTS ingestion procedure

### Step 1 — Identify the logical batch

For April 2026:

```text
batch_key = bts_reporting_carrier_ontime|2026|04
```

`batch_key` identifies the logical data batch and should remain stable across reruns of the same month.

### Step 2 — Start a new execution

Generate a new:

```text
run_id
load_id
```

These identify the execution and load attempt, not the business dataset.

### Step 3 — Read the raw BTS file

Expected April 2026 source baseline:

```text
597,919 rows
110 source columns
```

### Step 4 — Validate source expectations

Required checks:

- expected month only
- required fields present
- `FlightDate` parses
- candidate business-key fields are not null
- duplicate candidate-key groups measured

For the validated April source:

```text
20 / 20 required fields present
0 FlightDate parse failures
0 rows outside April
0 candidate-key null rows
0 duplicate candidate-key groups
```

### Step 5 — Compute/compare source hash

April validated SHA-256:

```text
71b1ac148bb7a344161b5eeb846aa662fae8d986b37025f8d8d92383b8c13ee7
```

If a previously loaded logical batch now has a different hash, treat it as a source mutation that requires explicit investigation rather than silently assuming it is the same batch.

### Step 6 — Write Bronze using controlled batch logic

Do not blind-append the same logical monthly batch.

The target behavior is:

```text
same logical batch rerun
→ same logical business state
```

while allowing new execution metadata.

### Step 7 — Reconcile

For the April baseline, success requires:

```text
source rows = 597,919
Bronze rows = 597,919
duplicate business-key groups = 0
required metadata nulls = 0
```

### Step 8 — Complete audit state

Record a successful load only after all required validation/reconciliation checks pass.

Expected lifecycle:

```text
STARTED
→ SUCCEEDED
```

On an unrecoverable error:

```text
STARTED
→ FAILED
```

---

## 7. BTS rerun procedure

Use this procedure when rerunning an unchanged monthly batch.

### Expected behavior

The same `batch_key` is reused.

New execution metadata is generated:

```text
new run_id
new load_id
```

The business result must remain unchanged.

For the validated April rerun:

```text
rows before = 597,919
rows after  = 597,919
source hash unchanged
duplicate business-key groups = 0
```

### Idempotency rule

A rerun is idempotent when:

```text
same logical input
→ same logical business state
```

`run_id`, `load_id`, timestamps, and audit entries may change because they describe the new execution.

### Failure condition

The rerun is not acceptable if it creates:

- duplicate logical flights
- additional rows from blind append
- unexpected source-hash mutation
- missing required lineage
- unreconciled source/target counts

---

## 8. Open-Meteo weather pilot procedure

### Current pilot scope

```text
ORD
ATL
April 2026
variable set = wx_v1
```

### Expected observation count

April contains 30 days:

```text
30 × 24 = 720 hourly observations per airport
```

### Request behavior

For each airport:

1. Read controlled airport configuration.
2. Use configured latitude/longitude.
3. Use the configured IANA timezone.
4. Request the approved historical variable set.
5. Use bounded retry only for transient failures.
6. Preserve the raw JSON response in OneLake.
7. Validate the response before publishing the Bronze row.
8. MERGE the Bronze response using its deterministic logical batch identity.
9. Append the load attempt to the audit table.

### Validated pilot result

```text
ORD = 720 hourly observations
ATL = 720 hourly observations
raw JSON files = 2
Bronze response rows = 2
required metadata nulls = 0
```

---

## 9. Weather retry policy

Retry transient technical failures such as:

```text
HTTP 429
HTTP 500
HTTP 502
HTTP 503
HTTP 504
temporary network timeout
```

The current design allows bounded retry with backoff/jitter, with up to 3 attempts for transient weather failures.

Do **not** endlessly retry deterministic/data-quality failures such as:

- malformed source structure
- missing required configuration
- invalid request parameters
- response that consistently violates the contract

Those failures require diagnosis or correction.

---

## 10. Retry vs idempotency

These concepts solve different problems.

### Retry

Answers:

```text
What should I do when an attempt fails temporarily?
```

Example:

```text
Open-Meteo returns HTTP 503
→ retry with bounded backoff
```

### Idempotency

Answers:

```text
What happens if I execute the logical operation again?
```

Example:

```text
rerun April BTS
→ still 597,919 logical Bronze rows
```

A pipeline should ideally have both.

---

## 11. Required post-run checks

### BTS

- [ ] expected source row count captured
- [ ] target row count reconciled
- [ ] required metadata non-null
- [ ] candidate-key duplicate groups measured
- [ ] source hash captured
- [ ] audit status correct
- [ ] rerun did not duplicate the logical batch

### Weather

- [ ] expected airport count processed
- [ ] 720 April hourly observations per airport
- [ ] raw JSON landed
- [ ] one Bronze response row per airport/month logical batch
- [ ] request/response metadata populated
- [ ] airport timezone captured
- [ ] audit row appended
- [ ] transient retries bounded

---

## 12. Recovery guidance

### BTS row-count mismatch

Do not mark the run successful.

Check:

1. raw-file row count
2. parsing behavior
3. filtering logic
4. batch-key scope
5. write/MERGE behavior
6. duplicate handling

### BTS source hash changed

Treat the source as mutated.

Do not silently overwrite without recording and understanding the change.

### Weather API transient error

Retry according to bounded retry policy.

### Weather response has incorrect hourly count

Do not publish it as a valid Bronze response.

Investigate:

- requested date range
- timezone
- API response structure
- missing/extra hourly arrays

### Audit row indicates failure

Preserve failure evidence. Correct the cause, then run a new attempt with a new `run_id`/`load_id` as appropriate.

---

## 13. Current operational boundaries

This runbook currently covers only the validated Week 3 Bronze scope.

Not yet covered:

- multi-month production scheduling
- Silver standardization
- Silver rejects/quarantine implementation
- Gold publication
- end-to-end orchestration across all medallion layers
- Direct Lake refresh behavior
- Power BI validation
- CI/CD deployment execution

The runbook should be extended as those capabilities are actually implemented.
