# AirOps 360 — Week 4 Silver Evidence

**Checkpoint:** Week 4 Silver implementation and end-to-end validation  
**Platform:** Microsoft Fabric  
**Workspace:** `AirOps 360`  
**Bronze Lakehouse:** `lh_airops_bronze`  
**Silver Lakehouse:** `lh_airops_silver`  
**Validation version:** `week4_silver_validation_v1`  
**Status:** PASS for the scoped April 2026 Silver implementation

---

## 1. Purpose

This document records the executed and independently revalidated Week 4 Silver evidence for AirOps 360.

The validated scope is intentionally limited to:

- April 2026 BTS flight standardization
- deterministic flight identity
- flight DQ and quarantine controls
- ORD/ATL April 2026 hourly weather normalization
- deterministic weather identity
- cardinality-safe origin-weather enrichment
- Bronze-to-Silver reconciliation
- persisted validation evidence

This checkpoint does **not** claim implementation of physical Gold tables, Direct Lake, Power BI, production multi-month backfill, or deployment pipelines.

---

## 2. Fabric notebooks in the validated Silver path

```text
nb_silver_standardize_flights
nb_silver_flight_key_dq_gate
nb_silver_normalize_weather
nb_silver_enrich_flights_weather
nb_silver_end_to_end_validation
```

The notebooks are versioned under:

```text
notebooks/silver/
```

---

## 3. Tables in scope

### Bronze inputs

```text
lh_airops_bronze.brz_bts_flights
lh_airops_bronze.brz_weather_api_raw
```

### Silver flight outputs

```text
slv_flights
slv_flights_validated
slv_flights_quarantine
slv_flights_dq_metrics
```

### Silver weather outputs

```text
slv_weather_hourly
```

### Silver enrichment outputs

```text
slv_flights_weather_enriched
slv_flights_weather_enrichment_metrics
```

### Week 4 validation evidence

```text
slv_week4_validation_metrics
```

---

## 4. Flight standardization evidence

Logical BTS batch:

```text
bts_reporting_carrier_ontime|2026|04
```

Validated counts:

| Check | Result |
|---|---:|
| Bronze flight rows | 597,919 |
| Standardized Silver rows | 597,919 |
| Standardization row-count delta | 0 |
| Flight-date parse failures | 0 |
| Rows outside April 2026 | 0 |
| Required Bronze lineage nulls | 0 |
| Type failures in required standardized fields | 0 |

Result:

```text
Bronze -> standardized Silver: PASS
```

The standardized dataset preserves the April source grain while converting selected flight, date, status, time, delay, distance, and lineage fields into controlled Silver types.

---

## 5. Flight identity, DQ, and quarantine evidence

### Deterministic business identity

`flight_key_v1` is the SHA-256 hash of a canonical representation of:

```text
flight_date
+ reporting_airline
+ flight_number
+ origin
+ dest
+ crs_dep_time_hhmm
```

The canonical material normalizes carrier and airport codes and pads scheduled departure time to four HHMM digits before hashing.

### Validated metrics

| Check | Result |
|---|---:|
| Bronze rows | 597,919 |
| Silver input rows | 597,919 |
| Structural-invalid rows | 0 |
| Duplicate rows quarantined | 0 |
| Accepted rows | 597,919 |
| Quarantine rows | 0 |
| Distinct accepted `flight_key` values | 597,919 |
| Accepted NULL `flight_key` values | 0 |
| Duplicate accepted `flight_key` groups | 0 |
| Independent key-recompute mismatches | 0 |
| Reconciliation | PASS |
| Accepted-key uniqueness | PASS |

Reconciliation invariant:

```text
Bronze rows = accepted rows + quarantine rows

597,919 = 597,919 + 0
```

Result:

```text
Deterministic flight identity + DQ gate: PASS
```

A zero-row quarantine for this April batch does not remove the control: the quarantine table and DQ rules remain part of the implemented path and are available to account for rejected records in future batches.

---

## 6. Weather normalization evidence

### Pilot scope

```text
Airports: ORD, ATL
Period:   2026-04-01 through 2026-04-30
```

Bronze grain:

```text
one source-preserving Open-Meteo airport/month response
```

Silver grain:

```text
one airport + one local observation hour
```

### Validated counts

| Check | ORD | ATL | Total |
|---|---:|---:|---:|
| Bronze response rows | — | — | 2 |
| Expected hourly rows | 720 | 720 | 1,440 |
| Observed hourly rows | 720 | 720 | 1,440 |

### Weather key and grain checks

| Check | Result |
|---|---:|
| Distinct `weather_key` values | 1,440 |
| NULL `weather_key` values | 0 |
| Duplicate local airport-hour groups | 0 |
| Duplicate UTC airport-hour groups | 0 |
| Independent weather-key recompute mismatches | 0 |

`weather_key_v1` is the SHA-256 hash of normalized:

```text
airport_code + weather_hour_local
```

### Weather-value checks

NULL count was zero for every validated weather variable:

```text
temperature_2m_c
relative_humidity_2m_pct
precipitation_mm
snowfall_cm
weather_code
cloud_cover_pct
wind_speed_10m_kmh
wind_direction_10m_deg
```

IANA timezone handling and local/UTC hourly timestamps were validated in the normalization notebook.

Result:

```text
Bronze weather -> hourly Silver weather: PASS
```

---

## 7. Weather-to-flight enrichment evidence

Join contract:

```text
accepted flight origin
+ scheduled departure local hour
        ->
weather airport_code
+ weather_hour_local
```

The weather side is validated as unique at airport-hour grain before joining.

The enrichment uses a LEFT JOIN so a flight is preserved even when weather is intentionally unavailable outside the current pilot scope.

### Cardinality checks

| Check | Result |
|---|---:|
| Accepted flight rows before join | 597,919 |
| Flight rows after join | 597,919 |
| Distinct `flight_key` before join | 597,919 |
| Distinct `flight_key` after join | 597,919 |
| Duplicate flight groups after join | 0 |
| Duplicate weather airport-hour groups | 0 |
| Wrong-airport matches | 0 |
| Wrong-hour matches | 0 |

Grain invariant:

```text
1 accepted flight_key -> at most 1 origin weather row
```

Result:

```text
597,919 flights in -> 597,919 flights out
```

No flight multiplication occurred.

---

## 8. Weather match reconciliation

Current weather coverage is deliberately limited to ORD and ATL.

| Match class | Rows |
|---|---:|
| ORD/ATL origin flights | 59,813 |
| ORD/ATL matched flights | 59,813 |
| ORD/ATL unmatched flights | 0 |
| Flights outside the ORD/ATL pilot | 538,106 |
| Total enriched flights | 597,919 |

Reconciliation:

```text
59,813 matched
+ 0 pilot-airport unmatched
+ 538,106 outside-pilot preserved
= 597,919 enriched flights
```

Flights outside ORD/ATL are not considered failed joins. They are preserved by design with weather columns left NULL because those origins are outside the current weather pilot.

---

## 9. Independent Week 4 validation gate

The end-to-end validation notebook re-read the current persisted Bronze and Silver state rather than relying only on earlier notebook success messages.

It independently revalidated:

- Bronze -> standardized -> accepted/quarantine counts
- persisted flight DQ metrics
- deterministic `flight_key` recomputation
- required flight lineage
- Bronze weather -> hourly Silver counts
- deterministic `weather_key` recomputation
- local and UTC weather uniqueness
- weather-value completeness
- weather-to-flight cardinality
- airport/hour match correctness
- persisted enrichment metrics

The notebook published 16 validation checks to:

```text
slv_week4_validation_metrics
```

All 16 checks have:

```text
status = PASS
validation_version = week4_silver_validation_v1
```

Executed validation timestamp recorded by Fabric:

```text
2026-09-21 01:28:16 UTC
```

Final notebook result:

```text
TASK 27 STATUS: PASS
```

---

## 10. End-to-end Silver evidence summary

```text
FLIGHTS
Bronze flight rows:              597,919
Standardized Silver rows:        597,919
Accepted Silver rows:            597,919
Quarantine rows:                 0
Distinct flight_key:             597,919
Flight-key recompute mismatches: 0

WEATHER
Bronze weather response rows:    2
Silver hourly weather rows:      1,440
ATL hourly rows:                 720
ORD hourly rows:                 720
Distinct weather_key:            1,440
Duplicate local airport-hours:   0
Duplicate UTC airport-hours:     0
Weather-key mismatches:          0

ENRICHMENT
Flight rows before join:         597,919
Flight rows after join:          597,919
Distinct flight_key after join:  597,919
Duplicate flight groups:         0
ORD/ATL weather matches:         59,813
ORD/ATL unmatched:               0
Outside-pilot flights preserved: 538,106
Wrong-airport matches:           0
Wrong-hour matches:              0
```

---

## 11. Reliability properties demonstrated

The scoped Bronze-to-Silver implementation now demonstrates:

- source-preserving Bronze ingestion
- explicit logical batch identity
- execution and load identity separated from business state
- source-to-target row reconciliation
- deterministic flight keys
- deterministic weather keys
- DQ reject/quarantine accounting
- lineage preservation
- local/UTC weather-time handling
- airport-hour uniqueness
- pre-join uniqueness gates
- left-join unmatched handling
- post-join row-count preservation
- post-join fact-grain preservation
- independently persisted validation evidence

---

## 12. Claims intentionally excluded

This Week 4 evidence package does **not** claim completion of:

- physical Gold Delta tables
- Gold incremental publication
- a completed star-schema load
- Direct Lake semantic modeling
- Power BI dashboard implementation
- multi-month production weather coverage
- all top-15 airports in Silver weather
- Fabric deployment pipelines
- production CI/CD

Gold dimensional **design** exists, but the physical Gold implementation remains pending.

---

## 13. Week 4 conclusion

The scoped Silver objective for April 2026 and the ORD/ATL weather pilot is validated:

```text
flight standardization              PASS
flight DQ / quarantine              PASS
deterministic flight identity       PASS
flight lineage preservation         PASS
hourly weather normalization        PASS
deterministic weather identity      PASS
weather airport-hour uniqueness     PASS
weather-to-flight enrichment        PASS
flight-grain preservation           PASS
Week 4 independent validation       PASS
```

The next implementation phase may proceed to the planned minimal Gold/serving slice without overstating Gold or BI completion.
