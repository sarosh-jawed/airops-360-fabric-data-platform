# AirOps 360

### Modern Aviation Analytics Platform on Microsoft Fabric

AirOps 360 is an end-to-end data engineering portfolio project that combines U.S. airline operational-performance data with historical weather data to analyze flight reliability, airport performance, carrier performance, and weather-related disruption.

> **Current status:** Bronze ingestion and the scoped April 2026 Silver pipeline are implemented and validated in Microsoft Fabric. Gold dimensional design is complete; physical Gold tables and Direct Lake / Power BI are not yet implemented.

---

## What is implemented

| Area | Status | Verified evidence |
|---|---|---|
| Source profiling | Complete | April 2026 BTS file: 597,919 rows, 110 columns, 20/20 required fields present |
| Airport/weather scope | Complete | Versioned top-15 airport configuration with IATA code, coordinates, IANA timezone, rank, and active flag |
| Bronze design | Complete | Versioned ingestion contract, deterministic batch identity, lineage metadata, audit model, rerun behavior, retry rules |
| Fabric Bronze environment | Complete | `AirOps 360` workspace, `lh_airops_bronze` Lakehouse, raw/reference paths, Bronze Delta tables |
| BTS Bronze ingestion | Complete | 597,919 April flight rows loaded; 110 source + 10 lineage columns; required metadata nulls 0 |
| BTS idempotent rerun | Complete | Rerun preserved 597,919 business rows; source hash unchanged; duplicate business-key groups 0 |
| Open-Meteo Bronze pilot | Complete | ORD + ATL, April 2026; 720 hourly observations per airport; 2 raw JSON files; 2 Bronze response rows |
| Silver flight standardization | Complete | 597,919 Bronze rows -> 597,919 standardized rows; required date/type/lineage validation passed |
| Silver flight key + DQ gate | Complete | 597,919 accepted; 0 quarantine; 597,919 distinct deterministic `flight_key`; 0 key-recompute mismatches |
| Silver hourly weather | Complete | 2 Bronze API responses -> 1,440 hourly rows; ATL 720 + ORD 720; unique deterministic airport-hour grain |
| Silver flight-weather enrichment | Complete | 597,919 accepted flights -> 597,919 enriched flights; 0 duplicate flight groups; 59,813/59,813 pilot-origin flights matched |
| Silver end-to-end validation | Complete | 16 persisted release checks all PASS in `slv_week4_validation_metrics` |
| Gold dimensional model | Design complete | `fact_flight_performance`, `dim_date`, `dim_airport`, `dim_carrier`, and load/audit concepts documented |
| Gold physical build | Not started | Design exists; physical Gold Delta tables are not yet implemented |
| Direct Lake / Power BI | Not started | Planned after a validated minimal Gold serving path |

This README intentionally distinguishes **implemented**, **validated**, **designed**, and **planned** work.

---

## Architecture

```text
BTS Reporting Carrier On-Time Performance        Open-Meteo Historical API
                    |                                      |
                    +------------------+-------------------+
                                       |
                                       v
                                  Bronze Layer
                        source-preserving + lineage
                                       |
                                       v
                                  Silver Layer
                standardized + DQ + deterministic keys
                                       |
                          +------------+------------+
                          |                         |
                          v                         v
                  validated flights          hourly weather
                          |                         |
                          +------------+------------+
                                       |
                                       v
                           cardinality-safe enrichment
                                       |
                                       v
                                   Gold Layer
                         dimensional analytical model
                         (design complete, build pending)
                                       |
                                       v
                              Direct Lake / Power BI
                                   (planned)
```

Detailed architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Bronze implementation

### Microsoft Fabric objects

- Workspace: `AirOps 360`
- Bronze Lakehouse: `lh_airops_bronze`
- Bronze notebooks:
  - `nb_bronze_environment_setup`
  - `nb_bronze_ingest_bts`
  - `nb_bronze_ingest_weather`

### Bronze Delta tables

```text
brz_bts_flights
brz_weather_api_raw
brz_ingestion_audit
```

### Raw/reference paths

```text
Files/raw/flights/year=YYYY/month=MM/
Files/raw/weather/airport=<AIRPORT>/year=YYYY/month=MM/
Files/reference/airports/airports_v0.1.csv
```

### Verified Bronze baseline

```text
BTS April rows:                    597,919
BTS source columns:                110
Bronze columns:                    120
Required Bronze metadata nulls:    0
Idempotent rerun rows before:      597,919
Idempotent rerun rows after:       597,919

Weather pilot:                     ORD, ATL
Expected/observed hours per site:  720
Raw JSON files:                    2
Bronze weather response rows:      2
```

Detailed Bronze evidence: [`docs/ingestion/WEEK3_BRONZE_EVIDENCE.md`](docs/ingestion/WEEK3_BRONZE_EVIDENCE.md)

Bronze operations: [`docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md`](docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md)

---

## Silver implementation

### Microsoft Fabric objects

- Silver Lakehouse: `lh_airops_silver`
- Silver notebooks:
  - `nb_silver_standardize_flights`
  - `nb_silver_flight_key_dq_gate`
  - `nb_silver_normalize_weather`
  - `nb_silver_enrich_flights_weather`
  - `nb_silver_end_to_end_validation`

### Silver tables

```text
slv_flights
slv_flights_validated
slv_flights_quarantine
slv_flights_dq_metrics
slv_weather_hourly
slv_flights_weather_enriched
slv_flights_weather_enrichment_metrics
slv_week4_validation_metrics
```

---

## Verified Week 4 Silver evidence

### Flights

```text
Bronze flight rows:              597,919
Standardized Silver rows:        597,919
Accepted Silver rows:            597,919
Quarantine rows:                 0
Distinct flight_key:             597,919
Flight-key recompute mismatches: 0
Required accepted-lineage nulls: 0
```

`flight_key_v1` is a deterministic SHA-256 identity built from the canonical scheduled-flight business key:

```text
flight_date
+ reporting_airline
+ flight_number
+ origin
+ dest
+ crs_dep_time_hhmm
```

The core reconciliation is:

```text
597,919 Bronze
=
597,919 accepted
+
0 quarantine
```

### Weather

Current validated pilot:

```text
Airports: ORD, ATL
Period:   April 2026
```

Evidence:

```text
Bronze weather responses:        2
Silver hourly weather rows:      1,440
ATL hourly rows:                 720
ORD hourly rows:                 720
Distinct weather_key:            1,440
Duplicate local airport-hours:   0
Duplicate UTC airport-hours:     0
Weather-key recompute mismatches:0
Required weather-value NULLs:    0
```

Silver weather grain:

```text
one airport + one local observation hour
```

### Weather-to-flight enrichment

Join contract:

```text
flight origin + scheduled local departure hour
    ->
weather airport + local observation hour
```

Evidence:

```text
Accepted rows before join:         597,919
Enriched rows after join:          597,919
Distinct flight_key after join:    597,919
Duplicate flight groups after:     0

ORD/ATL origin flights:            59,813
ORD/ATL matched flights:           59,813
ORD/ATL unmatched flights:         0
Outside-pilot flights preserved:   538,106

Wrong-airport matches:             0
Wrong-hour matches:                0
```

The enrichment uses a LEFT JOIN. Flights outside the current ORD/ATL weather pilot remain in the dataset with NULL weather columns.

The validated grain invariant is:

```text
1 accepted flight_key -> at most 1 origin weather row
```

### Independent Silver release gate

`nb_silver_end_to_end_validation` independently re-read the persisted Bronze/Silver tables, recomputed deterministic keys, rechecked uniqueness and cardinality, and published 16 PASS checks to:

```text
slv_week4_validation_metrics
```

Validation version:

```text
week4_silver_validation_v1
```

Final result:

```text
TASK 27 STATUS: PASS
```

Detailed evidence: [`docs/silver/WEEK4_SILVER_EVIDENCE.md`](docs/silver/WEEK4_SILVER_EVIDENCE.md)

Silver operations: [`docs/silver/SILVER_OPERATIONS_RUNBOOK.md`](docs/silver/SILVER_OPERATIONS_RUNBOOK.md)

---

## Reliability controls demonstrated

AirOps currently demonstrates:

- deterministic logical `batch_key`
- unique execution `run_id`
- source-object `load_id`
- source hashing for mutation detection
- idempotent Bronze reruns
- source-to-target reconciliation
- deterministic `flight_key`
- deterministic `weather_key`
- DQ quarantine accounting
- lineage preservation
- local/UTC weather-time handling
- weather airport-hour uniqueness
- pre-join uniqueness validation
- cardinality-safe LEFT JOIN enrichment
- explicit outside-pilot match status
- post-join row-count and flight-grain validation
- persisted transformation metrics
- independent end-to-end Silver release validation

The central reliability principles are:

> The same logical input should reproduce the same logical business state, even when execution metadata changes.

and:

> An enrichment must not silently change the grain of the dataset it enriches.

---

## Gold model design

The Gold v0.1 design is complete but not yet physically implemented.

Primary analytical fact:

```text
fact_flight_performance
grain = one scheduled carrier flight occurrence
```

Dimensions:

- `dim_date`
- `dim_airport`
- `dim_carrier`

`dim_airport` is role-played through origin and destination foreign keys.

The selected origin-weather measurements are designed to be carried at flight grain using the already validated Silver origin airport + scheduled departure-hour enrichment.

See [`docs/modeling/GOLD_STAR_SCHEMA_V0.1.md`](docs/modeling/GOLD_STAR_SCHEMA_V0.1.md).

---

## Data sources

### Airline operations

U.S. Department of Transportation  
Bureau of Transportation Statistics  
Reporting Carrier On-Time Performance

### Weather

Open-Meteo Historical Weather API

See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

---

## Key documentation

- [`docs/PROJECT_SCOPE.md`](docs/PROJECT_SCOPE.md) — project boundaries and MVP scope
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — end-to-end architecture
- [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md) — source contracts, grains, keys, and quality rules
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — source definitions and airport/weather scope
- [`docs/profiling/BTS_2026_04_PROFILE.md`](docs/profiling/BTS_2026_04_PROFILE.md) — April BTS profiling evidence
- [`docs/ingestion/BRONZE_INGESTION_DESIGN_V0.1.md`](docs/ingestion/BRONZE_INGESTION_DESIGN_V0.1.md) — Bronze ingestion design
- [`docs/ingestion/WEEK3_BRONZE_EVIDENCE.md`](docs/ingestion/WEEK3_BRONZE_EVIDENCE.md) — verified Week 3 Bronze evidence
- [`docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md`](docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md) — Bronze operating procedure
- [`docs/silver/WEEK4_SILVER_EVIDENCE.md`](docs/silver/WEEK4_SILVER_EVIDENCE.md) — verified Week 4 Silver evidence
- [`docs/silver/SILVER_OPERATIONS_RUNBOOK.md`](docs/silver/SILVER_OPERATIONS_RUNBOOK.md) — Silver operating and recovery procedure
- [`docs/modeling/GOLD_STAR_SCHEMA_V0.1.md`](docs/modeling/GOLD_STAR_SCHEMA_V0.1.md) — Gold star-schema design
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — implementation roadmap

---

## Current limitations

The following items are intentionally **not** claimed as implemented:

- physical Gold Delta tables
- Gold incremental publication
- Direct Lake semantic model
- Power BI dashboard
- production multi-month flight/weather orchestration
- Silver weather coverage for all configured top-15 airports
- Fabric deployment pipeline implementation
- production CI/CD

The current validated Silver evidence is for **April 2026 flights** and the **ORD/ATL April weather pilot**.

---

## Next implementation phase

1. Preserve the Week 4 Silver evidence and notebook in Git.
2. Build one minimal validated Gold flight-performance serving path.
3. Reconcile accepted Silver `flight_key` values into Gold.
4. Connect the minimal Gold/semantic path to Power BI.
5. Capture recruiter-ready Gold/BI evidence without weakening existing Silver controls.
6. Expand scope only after the minimal end-to-end serving slice is validated.

---

## License

This repository contains original project code and documentation released under the MIT License.

Source datasets remain subject to their respective source terms.
