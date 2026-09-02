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

**Project airport scope (v0.1):** The weather-enrichment scope is frozen to the top 15 origin airports observed in the April 2026 BTS Reporting Carrier On-Time Performance profile.

**Selection evidence:** `docs/profiling/BTS_2026_04_PROFILE.md`

**Airport reference configuration:** `config/airports_v0.1.csv`

The v0.1 airport scope is:

1. ORD
2. ATL
3. DFW
4. DEN
5. PHX
6. LAX
7. CLT
8. LAS
9. MCO
10. SEA
11. BOS
12. SFO
13. DCA
14. LGA
15. DTW

The ranking is based on April 2026 BTS origin-flight counts in descending order.

Each configured airport includes:

- IATA airport code
- decimal-degree latitude
- decimal-degree longitude
- IANA timezone
- April origin-volume rank
- active flag

Coordinates are used for Open-Meteo weather requests.

IANA timezones are required because BTS scheduled and actual flight times are airport-local. Weather observations must therefore be aligned to the airport's local time before UTC normalization or flight-weather joining.

All 15 airports are active in scope v0.1.

Future airport additions, removals, or deactivations must be explicit configuration changes supported by profiling or project-scope evidence. Airport scope must not change silently between pipeline runs.

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
