# AirOps 360 - Data Sources

## Bureau of Transportation Statistics

**Dataset:** Reporting Carrier On-Time Performance

**Purpose:** Primary airline operational dataset.

**Project period:** April 2026 through June 2026.

**Usage:** Flight operations, schedules, delays, cancellations, diversions, airport and carrier performance.

**Official source:** U.S. Department of Transportation Bureau of Transportation Statistics.

**Raw data policy:** Large raw files are not stored in GitHub.

---

## Open-Meteo Historical Weather API

**Purpose:** Hourly historical weather enrichment for selected airports.

**Project airport scope:** Approximately 15 high-volume airports represented in the flight dataset. The final airport list will be established after BTS source profiling.

**Contracted weather variables:**

- `temperature_2m`
- `precipitation`
- `rain`
- `snowfall`
- `weather_code`
- `wind_speed_10m`
- `wind_gusts_10m`
- `visibility` only when consistently available

Raw API responses are persisted to the Bronze layer but are not stored in the GitHub repository except for small sanitized samples.

---

## Data Contract

The field-level source agreement, grains, deterministic keys, refresh boundaries, raw-file conventions, time-zone rules, quality expectations, and ingestion metadata are defined in:

`docs/DATA_CONTRACT.md`

The contract is authoritative for implementation assumptions until source profiling proves that an assumption must change.
