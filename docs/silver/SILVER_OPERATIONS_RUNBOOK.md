# AirOps 360 — Silver Operations Runbook

**Scope:** Validated Week 4 Silver implementation  
**Platform:** Microsoft Fabric  
**Workspace:** `AirOps 360`  
**Bronze Lakehouse:** `lh_airops_bronze`  
**Silver Lakehouse:** `lh_airops_silver`

---

## 1. Purpose

This runbook defines the repeatable execution and validation procedure for the currently implemented AirOps 360 Silver path.

It covers:

- flight standardization
- deterministic flight identity
- flight DQ and quarantine
- hourly weather normalization
- weather-to-flight enrichment
- end-to-end Silver reconciliation
- failure gates and recovery guidance

It does not describe physical Gold, Direct Lake, or Power BI execution because those capabilities are not yet validated as implemented.

---

## 2. Current Silver notebooks

Run the notebooks in this order:

```text
1. nb_silver_standardize_flights
2. nb_silver_flight_key_dq_gate
3. nb_silver_normalize_weather
4. nb_silver_enrich_flights_weather
5. nb_silver_end_to_end_validation
```

The final validation notebook is a release gate. Do not treat the Silver state as validated after changing upstream data or logic until it passes again.

---

## 3. Current tables

### Bronze inputs

```text
lh_airops_bronze.brz_bts_flights
lh_airops_bronze.brz_weather_api_raw
```

### Silver flight tables

```text
slv_flights
slv_flights_validated
slv_flights_quarantine
slv_flights_dq_metrics
```

### Silver weather table

```text
slv_weather_hourly
```

### Enrichment tables

```text
slv_flights_weather_enriched
slv_flights_weather_enrichment_metrics
```

### End-to-end validation table

```text
slv_week4_validation_metrics
```

---

## 4. Validated operating scope

### Flight batch

```text
batch_key = bts_reporting_carrier_ontime|2026|04
expected rows = 597,919
```

### Weather pilot

```text
airports = ORD, ATL
period = 2026-04-01 through 2026-04-30
expected hours per airport = 720
expected Silver weather rows = 1,440
```

Do not expand airport or month scope silently. A scope change requires a new validation baseline.

---

## 5. Preflight checklist

Before running Silver:

- [ ] Bronze April BTS batch exists and contains 597,919 rows.
- [ ] Bronze weather contains the intended ORD and ATL April responses.
- [ ] `lh_airops_bronze` is available to the notebooks that read cross-Lakehouse inputs.
- [ ] `lh_airops_silver` is the intended Silver target.
- [ ] The current notebook versions in Git match the code being executed in Fabric.
- [ ] No unreviewed change has been made to business-key fields.
- [ ] No unreviewed change has been made to weather timezone logic.
- [ ] No unreviewed change has been made to weather join grain.

If any contract changes, rerun the complete end-to-end validation.

---

## 6. Step 1 — Standardize flights

Run:

```text
nb_silver_standardize_flights
```

Input:

```text
lh_airops_bronze.brz_bts_flights
```

Output:

```text
slv_flights
```

### Required checks

For the validated April batch:

```text
Bronze rows = 597,919
Silver rows = 597,919
FlightDate parse failures = 0
Rows outside April 2026 = 0
Required Bronze lineage nulls = 0
Required type failures = 0
```

### Stop conditions

Do not continue if:

- row count changes unexpectedly
- required lineage is missing
- required dates fail parsing
- malformed HHMM values are detected
- required target types fail validation

---

## 7. Step 2 — Flight key, DQ, dedupe, and quarantine

Run:

```text
nb_silver_flight_key_dq_gate
```

Inputs:

```text
lh_airops_bronze.brz_bts_flights
slv_flights
```

Outputs:

```text
slv_flights_validated
slv_flights_quarantine
slv_flights_dq_metrics
```

### Flight business identity

`flight_key_v1` is derived deterministically from:

```text
flight_date
reporting_airline
flight_number
origin
dest
crs_dep_time_hhmm
```

The key is SHA-256 over canonicalized key material.

### Required invariants

```text
Bronze rows = accepted rows + quarantine rows
accepted flight_key NULLs = 0
accepted duplicate flight_key groups = 0
recomputed flight_key mismatches = 0
```

Validated April result:

```text
597,919 = 597,919 + 0
```

### Stop conditions

Do not publish accepted Silver if:

- structural-invalid rows are unexplained
- accepted + quarantine does not reconcile to input
- accepted keys contain NULL
- accepted keys are duplicated
- recomputed keys do not match persisted keys

A non-zero quarantine is not automatically a pipeline failure. It becomes a failure when rejected rows are unaccounted for or violate the agreed acceptance policy.

---

## 8. Step 3 — Normalize hourly weather

Run:

```text
nb_silver_normalize_weather
```

Input:

```text
lh_airops_bronze.brz_weather_api_raw
```

Output:

```text
slv_weather_hourly
```

### Required grain

```text
one airport + one local observation hour
```

### Required pilot counts

```text
ORD = 720
ATL = 720
total = 1,440
```

### Required checks

- [ ] Bronze pilot response rows = 2.
- [ ] JSON parses successfully.
- [ ] Time arrays and weather-variable arrays have expected cardinality.
- [ ] Open-Meteo units match the expected contract.
- [ ] Local timezone and UTC timestamps are populated correctly.
- [ ] `weather_key` is non-null.
- [ ] `weather_key` is unique.
- [ ] `(airport_code, weather_hour_local)` is unique.
- [ ] `(airport_code, weather_hour_utc)` is unique.
- [ ] Required weather values are non-null.

### Stop conditions

Do not continue to enrichment if the weather side is not unique at the intended join grain.

---

## 9. Step 4 — Enrich accepted flights with origin weather

Run:

```text
nb_silver_enrich_flights_weather
```

Inputs:

```text
slv_flights_validated
slv_weather_hourly
```

Outputs:

```text
slv_flights_weather_enriched
slv_flights_weather_enrichment_metrics
```

### Join contract

Flight join columns:

```text
origin
origin_sched_dep_hour_local
```

Weather join columns:

```text
airport_code
weather_hour_local
```

The weather uniqueness gate must pass **before** the join.

### Join type

```text
LEFT JOIN
```

Rationale:

- preserve every accepted flight
- enrich in-scope airport-hours when a weather row exists
- preserve outside-pilot flights with NULL weather fields
- never silently discard flights because weather coverage is intentionally limited

### Required cardinality checks

```text
flight rows before = flight rows after
distinct flight_key before = distinct flight_key after
duplicate flight groups after = 0
wrong-airport matches = 0
wrong-hour matches = 0
```

Validated April result:

```text
before = 597,919
after  = 597,919
```

### Match-status reconciliation

Validated pilot:

```text
MATCHED = 59,813
PILOT_AIRPORT_HOUR_UNMATCHED = 0
OUTSIDE_WEATHER_PILOT_AIRPORT = 538,106
```

Required equation:

```text
MATCHED
+ PILOT_AIRPORT_HOUR_UNMATCHED
+ OUTSIDE_WEATHER_PILOT_AIRPORT
= total enriched flights
```

---

## 10. Step 5 — Run the Silver release gate

Run:

```text
nb_silver_end_to_end_validation
```

Output:

```text
slv_week4_validation_metrics
```

This notebook must independently inspect the current persisted state.

It must verify:

- Bronze-to-standardized row equality
- accepted/quarantine reconciliation
- persisted DQ metrics
- independent `flight_key` recomputation
- accepted lineage
- Bronze-to-Silver weather counts
- independent `weather_key` recomputation
- local and UTC airport-hour uniqueness
- weather-value completeness
- enrichment cardinality
- airport/hour match correctness
- persisted enrichment metrics

### Validated baseline

```text
Bronze flights:                    597,919
Standardized flights:              597,919
Accepted flights:                  597,919
Quarantine rows:                   0
Distinct flight_key:               597,919
Flight-key recompute mismatches:   0

Bronze weather responses:          2
Silver weather rows:               1,440
ATL rows:                          720
ORD rows:                          720
Distinct weather_key:              1,440
Duplicate local airport-hours:     0
Duplicate UTC airport-hours:       0
Weather-key recompute mismatches:  0

Enriched flights:                  597,919
Duplicate enriched flight groups:  0
Pilot weather matches:             59,813
Pilot unmatched:                   0
Outside-pilot preserved:           538,106
Wrong-airport matches:             0
Wrong-hour matches:                0
```

Success requires:

```text
TASK 27 STATUS: PASS
```

---

## 11. Why persisted metrics and independent validation both exist

Persisted transformation metrics answer:

```text
What did the transformation report when it ran?
```

Independent release validation answers:

```text
What do the persisted tables actually contain now?
```

Both are required because a table can be changed after an earlier successful run.

---

## 12. Rerun procedure

For an unchanged logical April batch:

1. Confirm the Bronze logical batch is unchanged.
2. Run Silver standardization.
3. Run the flight DQ/key gate.
4. Run weather normalization for the same pilot scope.
5. Run weather enrichment.
6. Run end-to-end validation.
7. Compare all key counts to the validated baseline.
8. Publish or update evidence only after the release gate passes.

A rerun is acceptable when the same logical source state produces the same logical Silver business state. Processing timestamps may change.

---

## 13. Recovery guidance

### Flight counts do not reconcile

Stop downstream publication.

Check:

1. Bronze batch filter
2. standardization filters
3. DQ rules
4. duplicate handling
5. quarantine accounting
6. unexpected write mode or stale table state

Required equation:

```text
Bronze = accepted + quarantine
```

### `flight_key` recomputation mismatch

Treat as an identity-contract failure.

Check:

1. canonical key field list
2. case normalization
3. whitespace trimming
4. scheduled HHMM padding
5. hash algorithm/version
6. accidental transformation of a key component

Do not patch the hash value directly.

### Weather count is not 720 per pilot airport

Check:

1. requested date range
2. response timezone
3. hourly-array length
4. JSON parsing
5. missing/extra source observations
6. accidental filtering

### Duplicate weather airport-hour rows exist

Do not perform the flight-weather join.

Resolve the weather grain first. Joining a non-unique weather side can multiply flight rows.

### Flight count increases after enrichment

Treat as a cardinality failure.

Check:

1. weather airport-hour uniqueness
2. join columns
3. timezone alignment
4. hidden duplicate weather rows
5. accidental many-to-many join conditions

Required invariant:

```text
one accepted flight_key -> at most one weather row
```

### Pilot airport has unmatched weather rows

Investigate:

1. scheduled departure-hour derivation
2. local timezone conversion
3. requested weather period
4. airport code normalization
5. missing weather hours

Do not relabel an in-scope unmatched row as outside-pilot.

### Outside-pilot flights have NULL weather

This is expected under the current pilot.

Do not treat these rows as errors:

```text
OUTSIDE_WEATHER_PILOT_AIRPORT
```

They must remain in the dataset.

---

## 14. Change-control rules

Rerun the full Silver validation after changing any of the following:

- business-key fields
- key canonicalization
- flight DQ rules
- quarantine policy
- time parsing
- weather variable set
- timezone conversion
- weather key definition
- weather airport/month scope
- flight-weather join keys
- enrichment match-status rules
- Delta write strategy

If a change intentionally alters the validated baseline, version the contract and update the evidence document rather than silently editing historical values.

---

## 15. Current operational boundaries

The Silver runbook currently validates only:

```text
BTS flights: April 2026
Weather: ORD + ATL, April 2026
```

Not yet covered as completed production behavior:

- multi-month flight scheduling
- weather coverage for all configured airports
- physical Gold publication
- Gold incremental MERGE
- Direct Lake
- Power BI
- deployment pipelines
- production CI/CD

---

## 16. Silver release criterion

The Silver state is ready for the next implementation phase only when all of the following are true:

```text
Bronze -> Silver reconciliation         PASS
accepted/quarantine accounting          PASS
deterministic flight identity           PASS
flight lineage                          PASS
weather normalization                   PASS
weather airport-hour uniqueness         PASS
deterministic weather identity          PASS
weather enrichment cardinality          PASS
match correctness                       PASS
end-to-end validation evidence          PASS
```

For the current Week 4 April/ORD/ATL implementation, all criteria passed.
