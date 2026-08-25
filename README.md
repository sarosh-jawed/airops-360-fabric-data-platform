# ✈️ AirOps 360

### Modern Aviation Analytics Platform on Microsoft Fabric

AirOps 360 is an end-to-end data engineering portfolio project that combines U.S. airline operational performance data with historical weather data to analyze flight reliability, airport performance, carrier performance, and weather-related disruption.

> Status: 🚧 In development

---

## Project Objective

Build a production-style analytics pipeline demonstrating:

- Microsoft Fabric
- OneLake
- Fabric Lakehouse
- Delta Lake
- PySpark
- SQL
- Fabric Data Pipelines
- Medallion Architecture
- Incremental Processing
- Data Quality
- Reconciliation
- Direct Lake
- Power BI
- Git / CI

---

## Architecture

```text
BTS Flight Data                  Open-Meteo API
       │                               │
       └──────────────┬────────────────┘
                      ▼
                 Ingestion
                      │
                      ▼
                   Bronze
                  Raw Data
                      │
                      ▼
                   Silver
          Validated + Standardized
                      │
                      ▼
                    Gold
           Analytics-Ready Model
                      │
                      ▼
             Direct Lake / Power BI
```

A detailed architecture diagram will be maintained in:

`docs/ARCHITECTURE.md`

---

## Business Questions

AirOps 360 will investigate:

-  Which airports experience the most operational disruption? 
-  Which carriers provide the strongest on-time performance? 
-  How does weather correlate with flight delays? 
-  Which routes have persistent reliability problems? 
-  What delay causes contribute most to poor performance? 
-  Which airports are most sensitive to adverse weather? 

---

## Data Sources

### Airline Operations

U.S. Department of Transportation

Bureau of Transportation Statistics

Reporting Carrier On-Time Performance

### Weather

Open-Meteo Historical Weather API

See:

`docs/DATA_SOURCES.md`

---

## Data Architecture

AirOps 360 follows a medallion architecture:

### Bronze

Raw source preservation.

### Silver

Validated, standardized, deduplicated and weather-enriched data.

### Gold

Curated dimensional datasets optimized for analytics.

---

## Repository Structure

```
.
├── .github/workflows
├── config
├── data/sample
├── docs
├── notebooks
│   ├── bronze
│   ├── silver
│   └── gold
├── pipelines
├── powerbi
├── sql
├── src
│   ├── ingestion
│   ├── quality
│   ├── transformation
│   └── utils
└── tests
```

---

## Project Scope

The controlling requirements and scope document is:

`docs/PROJECT_SCOPE.md`

Any feature not defined there should be treated as out of scope until the MVP is complete.

---

## Planned Deliverables

-  Architecture diagram 
-  BTS ingestion 
-  Weather API ingestion 
-  Bronze layer 
-  Silver transformations 
-  Gold dimensional model 
-  Incremental processing 
-  Data-quality framework 
-  Reconciliation reporting 
-  Pipeline orchestration 
-  Direct Lake semantic model 
-  Power BI report 
-  Automated tests 
-  CI workflow 
-  Final technical documentation 

---

## Current Status

### Week 1

-  Repository scaffold 
-  Project scope 
-  Initial documentation 
-  Architecture v0.1 
-  Initial source profiling 

---

## License

This repository contains original project code and documentation released under the MIT License.

Source datasets remain subject to their respective source terms.
