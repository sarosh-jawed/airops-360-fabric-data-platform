# AirOps 360

### Modern Aviation Analytics Platform on Microsoft Fabric

AirOps 360 is an end-to-end data engineering portfolio project that combines U.S. airline operational-performance data with historical weather data to analyze flight reliability, airport performance, carrier performance, and weather-related disruption.

> **Current status:** Bronze ingestion implemented and validated in Microsoft Fabric. Gold dimensional design is complete; Silver transformation and Gold physical build are next.

---

## What is implemented

| Area | Status | Verified evidence |
|---|---|---|
| Source profiling | Complete | April 2026 BTS file: 597,919 rows, 110 columns, 20/20 required fields present |
| Airport/weather scope | Complete | Versioned top-15 airport configuration with IATA code, coordinates, IANA timezone, rank, and active flag |
| Bronze design | Complete | Versioned ingestion contract, deterministic batch identity, lineage metadata, audit model, rerun behavior, retry rules |
| Fabric Bronze environment | Complete | `AirOps 360` workspace, `lh_airops_bronze` Lakehouse, raw/reference paths, Bronze Delta tables |
| BTS Bronze ingestion | Complete | 597,919 April flight rows loaded; 110 source + 10 lineage columns; metadata-null count 0 |
| BTS idempotent rerun | Complete | Rerun preserved 597,919 business rows; source hash unchanged; duplicate business-key groups 0 |
| Open-Meteo Bronze pilot | Complete | ORD + ATL, April 2026; 720 hourly observations per airport; 2 raw JSON files; 2 Bronze response rows |
| Gold dimensional model | Design complete | `fact_flight_performance`, `dim_date`, `dim_airport`, `dim_carrier`, `ops_load_audit` documented |
| Silver transformation | Not started | Planned for the next implementation phase |
| Gold physical build | Not started | Design exists; Delta tables are not yet implemented |
| Direct Lake / Power BI | Not started | Planned after Gold implementation |

This README intentionally distinguishes **implemented**, **validated**, and **planned** work.

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
                     standardized + quality-controlled
                                       |
                                       v
                                   Gold Layer
                         dimensional analytical model
                                       |
                                       v
                              Direct Lake / Power BI
```

The detailed architecture is maintained in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Bronze implementation

### Microsoft Fabric objects

- Workspace: `AirOps 360`
- Lakehouse: `lh_airops_bronze`
- Fabric notebooks executed:
  - `nb_bronze_environment_setup`
  - `nb_bronze_ingest_bts`
  - `nb_bronze_ingest_weather`

### Bronze Delta tables

- `brz_bts_flights`
- `brz_weather_api_raw`
- `brz_ingestion_audit`

### Raw/reference paths

```text
Files/raw/flights/year=YYYY/month=MM/
Files/raw/weather/airport=<AIRPORT>/year=YYYY/month=MM/
Files/reference/airports/airports_v0.1.csv
```

---

## Verified Week 3 run evidence

### April 2026 BTS

Source profile:

```text
Rows:                  597,919
Source columns:        110
Required fields:       20 / 20 present
FlightDate failures:   0
Rows outside April:    0
Candidate-key nulls:   0
Duplicate key groups:  0
```

Initial Bronze load:

```text
Bronze rows:           597,919
Bronze columns:        120
                       = 110 source + 10 lineage/ingestion columns
Metadata nulls:        0
Source/Bronze match:   PASS
```

Idempotent rerun:

```text
Rows before:           597,919
Rows after:            597,919
Source hash:           unchanged
Duplicate key groups:  0
Business state:        unchanged
Execution metadata:    new run_id / load_id
Result:                PASS
```

### Open-Meteo pilot

Scope:

```text
Airports:              ORD, ATL
Period:                2026-04-01 through 2026-04-30
Expected hourly rows:  720 per airport
Observed hourly rows:  720 per airport
Raw JSON files:        2
Bronze response rows:  2
Metadata nulls:        0
Result:                PASS
```

The Bronze weather table intentionally stores one raw API response per airport/month batch. Hourly normalization is a Silver responsibility.

Detailed evidence: [`docs/ingestion/WEEK3_BRONZE_EVIDENCE.md`](docs/ingestion/WEEK3_BRONZE_EVIDENCE.md)

Operational procedure: [`docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md`](docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md)

---

## Reliability controls demonstrated

AirOps currently demonstrates the following Bronze-layer controls:

- deterministic logical `batch_key`
- unique execution `run_id`
- source-object attempt `load_id`
- source hash for mutation detection
- controlled batch replacement / MERGE behavior
- idempotent reruns
- source-to-Bronze row reconciliation
- duplicate business-key validation
- ingestion metadata validation
- STARTED / SUCCEEDED / FAILED audit states
- bounded retry for transient weather-API failures
- preservation of raw weather JSON for reproducibility

The key reliability principle is:

> Rerunning the same logical batch may create new execution metadata, but it must not create a different logical business state or duplicate business records.

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

Selected origin-weather measurements are planned to be carried at flight grain using origin airport + scheduled departure hour. A weather join must preserve one flight input row as one Gold flight row.

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
- [`docs/ingestion/WEEK3_BRONZE_EVIDENCE.md`](docs/ingestion/WEEK3_BRONZE_EVIDENCE.md) — verified Week 3 run evidence
- [`docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md`](docs/ingestion/BRONZE_OPERATIONS_RUNBOOK.md) — operational rerun/reconciliation procedure
- [`docs/modeling/GOLD_STAR_SCHEMA_V0.1.md`](docs/modeling/GOLD_STAR_SCHEMA_V0.1.md) — Gold star-schema design
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — current implementation roadmap

---

## Current limitations

The following items are intentionally **not** claimed as implemented yet:

- Silver flight standardization and deduplication
- Silver hourly weather normalization
- weather-to-flight enrichment
- physical Gold Delta tables
- end-to-end Gold incremental loading
- Direct Lake semantic model
- Power BI dashboard
- Fabric Git integration / deployment pipeline implementation
- automated CI test execution for the Fabric implementation

Fabric screenshots are not part of this Week 3 documentation checkpoint. Run evidence and reconciliation results are documented textually; screenshots can be added in a later portfolio-release pass.

---

## Next implementation phase

1. Build Silver standardized flight data.
2. Generate and validate deterministic `flight_key`.
3. Normalize airport-hour weather from preserved Bronze JSON.
4. Implement Silver data-quality and quarantine rules.
5. Build Gold dimensions and `fact_flight_performance`.
6. Reconcile accepted Silver business keys to Gold.
7. Add Direct Lake / Power BI after Gold validation.

---

## License

This repository contains original project code and documentation released under the MIT License.

Source datasets remain subject to their respective source terms.
