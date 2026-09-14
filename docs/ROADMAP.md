# AirOps 360 Roadmap

This roadmap reflects the **current implemented state** of the repository and Fabric project. A checked item means the work has been completed and validated; design-only work is labeled separately.

---

## Phase 1 — Foundation

- [x] Create repository scaffold
- [x] Define project requirements and scope
- [x] Create architecture v0.1
- [x] Profile April 2026 BTS dataset
- [x] Validate required source fields and provisional flight business key
- [x] Rank origin airports and finalize top-15 weather scope
- [x] Version airport reference configuration
- [x] Define data contract and raw path conventions

### Verified foundation evidence

```text
April 2026 BTS rows:          597,919
Source columns:               110
Required fields present:      20 / 20
Candidate-key null rows:      0
Duplicate candidate-key rows: 0
```

---

## Phase 2 — Bronze

- [x] Define Bronze ingestion design v0.1
- [x] Create Fabric workspace and Bronze Lakehouse
- [x] Create raw/reference OneLake paths
- [x] Create Bronze Delta table shells
- [x] Implement April BTS Bronze ingestion
- [x] Capture ingestion/lineage metadata
- [x] Reconcile April source rows to Bronze
- [x] Demonstrate idempotent April BTS rerun
- [x] Preserve source hash for mutation detection
- [x] Implement scoped Open-Meteo Bronze pilot for ORD + ATL
- [x] Preserve raw weather JSON
- [x] Validate 720 hourly observations per airport for April
- [x] Append Bronze audit evidence
- [x] Publish Week 3 Bronze evidence document
- [x] Publish Bronze operations runbook
- [ ] Add portfolio screenshots

### Bronze checkpoint

```text
BTS April rows:               597,919
BTS rerun rows:               597,919
BTS duplicate key groups:     0
Weather airports:             ORD, ATL
Weather observations/airport: 720
Raw weather JSON files:       2
Bronze weather response rows: 2
```

---

## Phase 3 — Silver

- [ ] Standardize flight data types and identifiers
- [ ] Generate deterministic `flight_key`
- [ ] Deduplicate standardized flight records
- [ ] Implement required quality gates
- [ ] Implement rejects/quarantine handling
- [ ] Normalize Bronze weather JSON to airport-hour grain
- [ ] Standardize local time handling
- [ ] Validate one airport + local observation hour grain
- [ ] Prepare weather data for Gold enrichment

---

## Phase 4 — Gold

### Design

- [x] Define Gold star-schema v0.1
- [x] Confirm `fact_flight_performance` grain
- [x] Define `dim_date`
- [x] Define role-playing `dim_airport`
- [x] Define `dim_carrier`
- [x] Define deterministic flight identity and surrogate-key strategy
- [x] Define origin-weather-at-flight-grain approach
- [x] Define Gold reconciliation/idempotency rules

### Physical implementation

- [ ] Create `dim_date`
- [ ] Create `dim_airport`
- [ ] Create `dim_carrier`
- [ ] Create `fact_flight_performance`
- [ ] Resolve stable dimension surrogate keys
- [ ] Join origin weather at scheduled departure hour
- [ ] Validate that weather enrichment does not multiply flight rows
- [ ] Reconcile accepted Silver flight keys to Gold

---

## Phase 5 — Production Engineering

### Demonstrated so far

- [x] Deterministic Bronze logical batch identity
- [x] New execution identity per rerun
- [x] Source hashing
- [x] Bronze row reconciliation
- [x] Idempotent BTS rerun
- [x] Bounded retry design for transient weather failures
- [x] Bronze audit-state design and pilot evidence

### Remaining

- [ ] Parameterize multi-month processing end to end
- [ ] Implement Silver incremental processing
- [ ] Implement Gold incremental MERGE
- [ ] Implement end-to-end reconciliation metrics
- [ ] Implement failure-path demo across the full pipeline
- [ ] Add automated tests for implemented Fabric transformations
- [ ] Implement Fabric Git integration workflow
- [ ] Implement deployment pipeline / Dev-Test-Prod promotion

---

## Phase 6 — Analytics

- [ ] Create Direct Lake semantic model
- [ ] Build Power BI dashboard
- [ ] Validate KPI definitions
- [ ] Reconcile report measures to Gold
- [ ] Document business findings

---

## Phase 7 — Portfolio Release

- [x] Make README reflect current implementation state
- [x] Publish textual Bronze run evidence
- [x] Publish Bronze operations runbook
- [ ] Add Fabric screenshots
- [ ] Add final architecture visuals
- [ ] Document Silver quality results
- [ ] Document Gold incremental run
- [ ] Add Direct Lake / Power BI evidence
- [ ] Record 3-minute project demo
- [ ] Add final project retrospective

---

## Current starting point

The next engineering phase is **Silver transformation and data quality**.

Bronze is considered complete for the scoped Week 3 checkpoint, but only ORD and ATL have been exercised through the weather API pilot. The project does not yet claim full weather backfill, Silver completion, Gold physical tables, Direct Lake, or Power BI implementation.
