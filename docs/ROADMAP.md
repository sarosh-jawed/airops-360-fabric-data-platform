\# AirOps 360 Roadmap



\## Phase 1 â€” Foundation



\- \[x] Create repository scaffold

\- \[x] Define project requirements and scope

- [x] Create architecture v0.1
\- \[ ] Profile BTS dataset

\- \[ ] Finalize airport/weather scope



\## Phase 2 â€” Bronze



\- \[ ] Build BTS file ingestion

\- \[ ] Build Open-Meteo API ingestion

\- \[ ] Add ingestion metadata

\- \[ ] Validate raw landing



\## Phase 3 â€” Silver



\- \[ ] Standardize flight data

\- \[ ] Build deterministic flight key

\- \[ ] Deduplicate records

\- \[ ] Standardize weather data

\- \[ ] Enrich flights with weather

\- \[ ] Add Silver quality checks



\## Phase 4 â€” Gold



\- \[ ] Create dim\_date

\- \[ ] Create dim\_airport

\- \[ ] Create dim\_carrier

\- \[ ] Create fact\_flight\_performance

\- \[ ] Validate dimensional model



\## Phase 5 â€” Production Engineering



\- \[ ] Parameterize monthly loads

\- \[ ] Implement incremental processing

\- \[ ] Demonstrate idempotent rerun

\- \[ ] Add reconciliation

\- \[ ] Add audit logging

\- \[ ] Add automated tests

\- \[ ] Add CI workflow



\## Phase 6 â€” Analytics



\- \[ ] Create Direct Lake semantic model

\- \[ ] Build Power BI dashboard

\- \[ ] Validate KPIs

\- \[ ] Document business findings



\## Phase 7 â€” Portfolio Release



\- \[ ] Finalize README

\- \[ ] Add screenshots

\- \[ ] Add architecture diagram

\- \[ ] Document quality results

\- \[ ] Document incremental run

\- \[ ] Add final project retrospective
---

## Week 2-3 Issue Board

### Week 2 - Source validation and Bronze foundation

- [ ] #2 Acquire and profile BTS flight-performance dataset
  - Validate required columns, data types, null rates, source row count, and provisional flight-key uniqueness.
  - Rank origin airports by flight volume.
- [ ] #3 Define airport reference dataset and weather scope
  - Freeze the approximately 15-airport MVP scope after profiling.
  - Store airport code, name, latitude, longitude, IANA time zone, rank, and active flag.
- [ ] #4 Implement Bronze BTS ingestion
  - Land April and May historical files using the documented Bronze path convention.
  - Capture run ID, contract version, batch key, source metadata, source count, and ingestion status.

### Week 3 - Weather, Silver quality, and incremental controls

- [ ] #5 Implement Open-Meteo historical weather ingestion
  - Use airport-local IANA time zones and the versioned weather-variable set.
  - Preserve raw responses and reproducible request parameters.
- [ ] #6 Implement Silver flight standardization and quality checks
  - Standardize types and identifiers, derive scheduled departure hour, generate the deterministic flight key, deduplicate, and quarantine invalid rows.
- [ ] #7 Design Gold dimensional model
  - Confirm fact grain and dimension keys against profiled source behavior before physical implementation.
- [ ] #8 Implement incremental load and reconciliation framework
  - Demonstrate June incremental processing, idempotent rerun behavior, source-to-Silver-to-Gold reconciliation, and operational audit metrics.

### Week 2-3 exit criteria

- Source assumptions in the data contract are validated or explicitly amended.
- The controlled airport reference is versioned.
- Bronze flight and weather ingestion are reproducible and auditable.
- Silver rejects and duplicate handling are measurable.
- June can be rerun without duplicate Gold business records.
- Reconciliation metrics explain accepted, rejected, duplicate, matched, unmatched, and published populations.