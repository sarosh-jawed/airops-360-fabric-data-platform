# AirOps 360 Data Contract

**Version:** 0.1  
**Status:** Accepted for implementation  
**Date:** 2026-08-26  
**Owner:** AirOps 360  
**Architecture:** `docs/ARCHITECTURE.md`  
**Scope authority:** `docs/PROJECT_SCOPE.md`

## 1. Purpose

This document defines the source-data contract for the AirOps 360 MVP.

A data contract is the agreement between a source and the pipeline about what data is expected, what one row means, which fields are required, how batches are identified, how files are named and stored, and what metadata must be captured so every load is reproducible and auditable.

This contract covers:

1. U.S. Department of Transportation Bureau of Transportation Statistics (BTS) flight-performance data.
2. Open-Meteo Historical Weather API data.
3. The controlled airport reference dataset used to connect airport codes to weather coordinates and time zones.

The contract intentionally separates **declared expectations** from **profiling results**. Field names, grains, keys, and validation rules are defined here, but assumptions such as business-key uniqueness must still be proven during source profiling.

---

## 2. Contract principles

- Bronze preserves source truth and lineage.
- No source record is silently discarded.
- Source batches are identifiable and rerunnable.
- Record-level business keys are deterministic.
- Critical fields and schemas are version controlled.
- Source-to-target counts are reconcilable.
- API request parameters required for reproducibility are stored.
- Raw source files and API payloads are not committed to GitHub except small sanitized samples.
- Contract changes that materially alter architecture or grain must be documented before implementation.

---

# 3. Source Contract A: BTS Flight Performance

## 3.1 Source identity

| Attribute | Contract |
|---|---|
| Source system | U.S. DOT Bureau of Transportation Statistics |
| Dataset | Reporting Carrier On-Time Performance |
| Source type | Monthly downloadable tabular file |
| MVP period | April 2026 through June 2026 |
| Historical baseline | April 2026 and May 2026 |
| Incremental demonstration batch | June 2026 |
| Bronze source name | `bts_reporting_carrier_ontime` |
| Contract version | `0.1` |

Official BTS reporting documentation defines carrier, flight number, origin, destination, flight date, scheduled/actual times, delay measures, cancellation information, and delay-cause measures. The TranStats download dataset exposes the Reporting Carrier On-Time Performance table for field-level extraction.

## 3.2 Expected source grain

**Expected source grain:**

```text
one reported scheduled carrier flight occurrence
```

A single source row represents one reported flight operation for a specific date, carrier, flight number, origin, destination, and schedule.

This expected grain will be confirmed during source profiling.

## 3.3 Required flight fields

These fields are required for the AirOps 360 MVP.

| Field | Logical type | Required | Purpose |
|---|---|---:|---|
| `FlightDate` | date | Yes | Flight operating date |
| `Reporting_Airline` | string | Yes | Reporting carrier identifier |
| `Flight_Number_Reporting_Airline` | string | Yes | Carrier flight number |
| `Origin` | string(3) | Yes | Origin airport code |
| `Dest` | string(3) | Yes | Destination airport code |
| `CRSDepTime` | HHMM-like source value | Yes | Scheduled departure time |
| `DepTime` | HHMM-like source value | No | Actual departure time |
| `DepDelay` | numeric minutes | No | Departure delay |
| `CRSArrTime` | HHMM-like source value | Yes | Scheduled arrival time |
| `ArrTime` | HHMM-like source value | No | Actual arrival time |
| `ArrDelay` | numeric minutes | No | Arrival delay |
| `Cancelled` | numeric/boolean-like | Yes | Cancellation indicator |
| `Diverted` | numeric/boolean-like | Yes | Diversion indicator |
| `AirTime` | numeric minutes | No | Airborne time |
| `Distance` | numeric | No | Flight distance |
| `CarrierDelay` | numeric minutes | No | Carrier-caused delay |
| `WeatherDelay` | numeric minutes | No | Weather-caused delay |
| `NASDelay` | numeric minutes | No | National Airspace System delay |
| `SecurityDelay` | numeric minutes | No | Security delay |
| `LateAircraftDelay` | numeric minutes | No | Late-arriving-aircraft delay |

### Important time rule

BTS reporting documentation defines scheduled and actual arrival/departure times in **local time**. AirOps 360 must therefore preserve the raw source time fields and explicitly derive timestamp/hour fields in Silver using airport time-zone context rather than treating HHMM values as UTC.

## 3.4 Candidate flight business key

The initial deterministic candidate key is:

```text
FlightDate
+ Reporting_Airline
+ Flight_Number_Reporting_Airline
+ Origin
+ Dest
+ CRSDepTime
```

Recommended canonical string before hashing:

```text
YYYY-MM-DD|CARRIER|FLIGHT_NUMBER|ORIGIN|DEST|HHMM
```

Recommended derived field:

```text
flight_key = SHA-256(canonical_business_key)
```

**Status:** provisional until source profiling confirms uniqueness.

If profiling finds collisions, the key must be revised and the change documented. The pipeline must not silently append arbitrary row numbers to hide a grain problem.

## 3.5 Batch and incremental key

BTS is treated as a monthly source.

**Source batch key:**

```text
source_name + load_year + load_month
```

Example:

```text
bts_reporting_carrier_ontime|2026|06
```

**Incremental boundary:**

```text
load_year + load_month
```

The June 2026 batch is the MVP incremental demonstration.

## 3.6 Raw-file convention

Recommended local/source filename after acquisition:

```text
bts_reporting_carrier_ontime_YYYY_MM.csv
```

Example:

```text
bts_reporting_carrier_ontime_2026_06.csv
```

Bronze landing convention:

```text
Files/raw/flights/year=YYYY/month=MM/
```

Example:

```text
Files/raw/flights/year=2026/month=06/
```

If the provider download is ZIP-compressed, preserve the original downloaded archive in the raw landing area when practical and record both archive name and extracted object name in ingestion metadata.

## 3.7 BTS structural validation

Hard-fail conditions before Silver publication:

- required columns are missing
- `FlightDate` cannot be parsed for a material portion of the source
- `Origin` or `Dest` schema is structurally incompatible with expected airport-code logic
- deterministic flight key cannot be generated
- the source file cannot be read

Row-level validation and quarantine candidates:

- missing `FlightDate`
- missing `Reporting_Airline`
- missing flight number
- missing `Origin`
- missing `Dest`
- malformed airport code
- invalid cancellation/diversion domain
- prohibited negative delay-cause values

Actual allowed domain values will be verified during source profiling rather than assumed from file type alone.

---

# 4. Source Contract B: Open-Meteo Historical Weather

## 4.1 Source identity

| Attribute | Contract |
|---|---|
| Source system | Open-Meteo |
| API | Historical Weather API |
| Endpoint family | `/v1/archive` |
| Source type | HTTPS JSON API |
| Geographic scope | Approximately 15 approved high-volume origin airports |
| Temporal grain | Hourly |
| MVP period | April 2026 through June 2026 |
| Bronze source name | `open_meteo_historical_weather` |
| Contract version | `0.1` |

Open-Meteo's Historical Weather API accepts latitude, longitude, start/end dates, time zone, and requested hourly variables. It returns location metadata, time-zone metadata, and hourly arrays.

## 4.2 Expected weather grain

**Expected Silver grain:**

```text
one airport + one local observation hour
```

Recommended unique key:

```text
airport_code + observation_local_timestamp
```

Recommended canonical representation:

```text
AIRPORT|YYYY-MM-DDTHH:00
```

## 4.3 Required request parameters

Every weather request must record or deterministically reconstruct:

| Parameter | Contract |
|---|---|
| `latitude` | From controlled airport reference |
| `longitude` | From controlled airport reference |
| `start_date` | First date of requested batch |
| `end_date` | Last date of requested batch |
| `hourly` | Versioned variable list |
| `timezone` | Airport-local IANA time zone from controlled reference |
| `timeformat` | `iso8601` |
| `temperature_unit` | `celsius` |
| `wind_speed_unit` | `kmh` |
| `precipitation_unit` | `mm` |

### Time-zone rule

The weather request must use an explicit airport-local time zone so weather observations align with BTS local scheduled departure times.

The response time zone and UTC offset must also be persisted as lineage metadata.

Do not depend on the Open-Meteo default GMT behavior for the production pipeline.

## 4.4 Required hourly variables

The MVP weather variable set is:

| API field | Logical type | Required | Purpose |
|---|---|---:|---|
| `time` | local timestamp | Yes | Observation hour |
| `temperature_2m` | decimal | Yes | Near-surface air temperature |
| `precipitation` | decimal | Yes | Total preceding-hour precipitation |
| `rain` | decimal | Yes | Liquid precipitation |
| `snowfall` | decimal | Yes | Snowfall amount |
| `weather_code` | integer | Yes | WMO weather condition code |
| `wind_speed_10m` | decimal | Yes | Wind speed at 10 m |
| `wind_gusts_10m` | decimal | Yes | Wind gust at 10 m |

`visibility` is treated as **optional** in contract v0.1. It may be added only if the selected historical API/model exposes it consistently for the project period. Its absence must not fail ingestion.

## 4.5 Weather batch key

Weather is requested by airport and monthly period.

**Request batch key:**

```text
source_name + airport_code + load_year + load_month + variable_set_version
```

Example:

```text
open_meteo_historical_weather|ORD|2026|06|wx_v1
```

## 4.6 Raw API file convention

Recommended raw response name:

```text
open_meteo_<AIRPORT>_YYYY_MM.json
```

Example:

```text
open_meteo_ORD_2026_06.json
```

Bronze landing convention:

```text
Files/raw/weather/airport=<AIRPORT>/year=YYYY/month=MM/
```

Example:

```text
Files/raw/weather/airport=ORD/year=2026/month=06/
```

One raw response should remain traceable to one airport/month request whenever practical.

## 4.7 Weather validation

Hard-fail request conditions:

- HTTP request fails after approved retry policy
- response cannot be parsed
- required response structure is missing
- `time` array is missing
- required hourly variables are missing from the payload

Quality checks:

- timestamp sequence is parseable
- airport reference exists
- response coordinates/time zone are recorded
- variable arrays align to the timestamp array length
- expected observation coverage is calculated for the requested local-time interval
- missing hours are counted and reported

Expected hourly count must be derived from the requested interval and time zone rather than permanently hard-coded to `24 × days`, because local time can include daylight-saving transitions.

---

# 5. Source Contract C: Airport Reference

## 5.1 Purpose

The airport reference is a controlled project-owned dataset used to bridge BTS airport codes and Open-Meteo coordinates/time zones.

## 5.2 Expected grain

```text
one approved airport code
```

## 5.3 Required fields

| Field | Logical type | Required | Purpose |
|---|---|---:|---|
| `airport_code` | string(3) | Yes | Join key to BTS Origin/Dest |
| `airport_name` | string | Yes | Human-readable label |
| `latitude` | decimal | Yes | Open-Meteo request coordinate |
| `longitude` | decimal | Yes | Open-Meteo request coordinate |
| `timezone_iana` | string | Yes | Local-time alignment |
| `scope_rank` | integer | Yes | Flight-volume scope ranking |
| `active_flag` | boolean | Yes | Controls weather ingestion scope |
| `effective_from` | date | Yes | Reference governance |
| `source_note` | string | No | Coordinate/reference provenance |

The actual top-15 airport list is **not declared complete by this contract**. It will be finalized after BTS source profiling.

---

# 6. Common ingestion metadata contract

Every ingestion run must capture the following operational metadata.

| Field | Required | Description |
|---|---:|---|
| `run_id` | Yes | Unique end-to-end pipeline execution ID |
| `contract_version` | Yes | Data contract version, initially `0.1` |
| `source_name` | Yes | Stable logical source identifier |
| `source_object` | Yes | File, API request, or reference object |
| `source_uri` | Yes when available | Provider/source location |
| `source_file_name` | Yes for file loads | Original or normalized file name |
| `load_year` | Yes | Logical load year |
| `load_month` | Yes | Logical load month |
| `batch_key` | Yes | Deterministic source batch identifier |
| `ingested_at_utc` | Yes | Bronze ingestion timestamp |
| `ingestion_status` | Yes | `STARTED`, `SUCCEEDED`, or `FAILED` |
| `source_row_count` | Yes when measurable | Raw source row/observation count |
| `processed_row_count` | Later stage | Count processed by current activity |
| `rejected_row_count` | Later stage | Count rejected/quarantined |
| `target_row_count` | Later stage | Target output count |
| `source_hash` | Recommended | File/content checksum when feasible |
| `error_message` | On failure | Failure detail |
| `pipeline_name` | Yes | Executing pipeline |
| `activity_name` | Yes | Ingestion activity/notebook |
| `parameters_json` | Recommended | Reproducible load/request parameters |

For API ingestion, `parameters_json` should include the non-secret parameters used to reproduce the request.

---

# 7. Bronze lineage requirements

Bronze must preserve enough information to answer:

```text
Where did this data come from?
Which source batch produced it?
When was it ingested?
Which pipeline run created it?
Which contract version governed it?
Can I reproduce the request/load?
```

Bronze does **not** need to enforce the final business model. Its primary responsibilities are source preservation, lineage, reproducibility, and reconciliation.

---

# 8. Refresh and incremental policy

## BTS

```text
Frequency: monthly source batches
Historical baseline: 2026-04, 2026-05
Incremental demonstration: 2026-06
Incremental key: year + month
Record key: provisional deterministic flight_key
```

## Open-Meteo

```text
Frequency: one request set per approved airport/month
Historical baseline: weather aligned to 2026-04 and 2026-05 flights
Incremental demonstration: weather aligned to 2026-06 flights
Incremental key: airport + year + month + variable-set version
Record key: airport + local observation timestamp
```

No source batch should be considered complete until its audit record has a terminal status and source count.

---

# 9. Reconciliation expectations

The contract supports the following reconciliation chain:

```text
BTS source rows
    ->
Bronze flight rows
    ->
Silver accepted + rejected + explicitly removed duplicates
    ->
Gold fact population
```

Weather reconciliation:

```text
Expected airport-hour observations
    ->
Bronze weather observations
    ->
Silver valid weather observations
    ->
Flight-weather matched + unmatched records
```

Unmatched weather enrichment is a measurable quality metric, not a silent data loss.

---

# 10. Schema-evolution policy

Contract v0.1 uses explicit required fields.

If a provider:

- removes a required field
- changes a required field meaning
- changes source grain
- changes key semantics
- materially changes time-zone behavior
- introduces incompatible schema changes

the pipeline must fail safely or quarantine the affected batch rather than silently reinterpret the source.

Any deliberate contract change increments the contract version and is recorded in project documentation.

Additive optional fields may be accepted without breaking the pipeline if they do not alter required semantics.

---

# 11. Data not stored in GitHub

The repository may contain only:

- small sanitized sample files
- schemas
- field dictionaries
- test fixtures
- configuration
- documentation

The following are excluded:

- production-sized BTS downloads
- full raw API history
- credentials or secrets
- environment-specific connection information

---

# 12. Definition of Done for Data Contract v0.1

Task 14 is complete when this document clearly defines:

- [x] BTS source identity
- [x] Open-Meteo source identity
- [x] expected source grains
- [x] required/key fields
- [x] provisional flight business key
- [x] weather observation key
- [x] monthly refresh/incremental boundaries
- [x] raw file and Bronze path conventions
- [x] airport reference contract
- [x] common ingestion metadata
- [x] time-zone handling
- [x] quality expectations
- [x] reconciliation expectations
- [x] schema-evolution behavior
- [x] GitHub raw-data policy

## 13. Next validation work

This contract defines what the pipeline expects. The next source-profiling tasks must validate the assumptions rather than rewriting them silently.

Next steps:

1. Acquire the April 2026 BTS source extract.
2. Profile column presence, types, null rates, row counts, and candidate-key uniqueness.
3. Rank origin airports by flight volume.
4. Finalize the approximately 15-airport weather scope.
5. Create the controlled airport reference dataset.
6. Run a small Open-Meteo request for one airport and validate the response against this contract.
