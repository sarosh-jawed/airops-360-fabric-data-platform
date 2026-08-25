\# AirOps 360 — Project Scope and Requirements



\## 1. Project Summary



AirOps 360 is an end-to-end Microsoft Fabric data engineering portfolio project that combines U.S. airline operational performance data with historical weather data.



The platform will demonstrate ingestion, medallion architecture, Delta Lake, PySpark, SQL, dimensional modeling, incremental processing, data-quality validation, reconciliation, orchestration, Direct Lake, Power BI, Git-based development, testing, and monitoring.



The project is intentionally scoped as a production-style portfolio implementation rather than a production airline system.



\---



\## 2. Primary Objective



Build a reproducible Microsoft Fabric analytics platform capable of answering:



\- Which airports and carriers experience the greatest delays?

\- How does weather relate to airline operational performance?

\- Which routes experience persistent reliability problems?

\- How do delay patterns change by airport, carrier, date, and time?

\- What factors contribute most strongly to flight delays?

\- Which airports appear most sensitive to adverse weather?



\---



\## 3. Primary Technology Stack



\### Platform

\- Microsoft Fabric

\- OneLake

\- Fabric Lakehouse



\### Data Engineering

\- Python

\- PySpark

\- Spark SQL

\- T-SQL

\- Delta Lake

\- Fabric Data Pipelines

\- Fabric Notebooks



\### Analytics

\- Power BI

\- Direct Lake

\- DAX



\### Engineering

\- Git

\- GitHub

\- pytest

\- GitHub Actions

\- configuration-driven processing

\- structured logging



\---



\## 4. Data Sources



\### 4.1 Airline Data



Source:

U.S. Department of Transportation Bureau of Transportation Statistics.



Dataset:

Reporting Carrier On-Time Performance.



Initial project window:

April 2026 through June 2026.



Load strategy:

\- April 2026: historical

\- May 2026: historical

\- June 2026: incremental load



Representative fields include:



\- FlightDate

\- Reporting\_Airline

\- Flight\_Number\_Reporting\_Airline

\- Origin

\- Dest

\- CRSDepTime

\- DepTime

\- DepDelay

\- CRSArrTime

\- ArrTime

\- ArrDelay

\- Cancelled

\- Diverted

\- AirTime

\- Distance

\- CarrierDelay

\- WeatherDelay

\- NASDelay

\- SecurityDelay

\- LateAircraftDelay



Raw source files will NOT be committed to GitHub.



\---



\### 4.2 Weather Data



Source:

Open-Meteo Historical Weather API.



Weather will be retrieved for approximately the top 15 airports represented in the flight dataset.



Representative hourly features:



\- temperature\_2m

\- precipitation

\- rain

\- snowfall

\- weather\_code

\- wind\_speed\_10m

\- wind\_gusts\_10m

\- visibility when available



Airport latitude/longitude will be maintained through a controlled airport reference dataset.



\---



\## 5. Architecture



The project follows a medallion architecture.



\### Bronze



Purpose:

Preserve raw source data with minimal transformation.



Contents:

\- BTS flight files

\- Open-Meteo API responses

\- ingestion metadata



Requirements:

\- preserve raw values

\- capture ingestion timestamp

\- capture source file/API information

\- partition logically by load period

\- support reruns without corrupting source data



\### Silver



Purpose:

Produce validated, standardized, deduplicated datasets.



Flight transformations include:

\- normalize column names

\- standardize data types

\- validate dates

\- validate airport codes

\- normalize carrier fields

\- deduplicate flights

\- generate flight business key

\- derive scheduled hour

\- derive delay indicators

\- handle cancelled/diverted records



Weather transformations include:

\- normalize API response

\- standardize timestamps

\- associate observations with airport

\- validate expected hourly observations



Weather is joined to scoped flight records using airport and time grain.



\### Gold



Purpose:

Create analytics-ready dimensional datasets.



Planned model:



\- fact\_flight\_performance

\- dim\_date

\- dim\_airport

\- dim\_carrier



Weather-derived attributes required for flight analysis will be included in the curated flight fact or supporting curated tables where appropriate.



\---



\## 6. Incremental Processing Requirement



The project must demonstrate incremental loading.



Historical baseline:

April-May 2026.



Incremental batch:

June 2026.



Requirements:



\- parameterized load period

\- monthly partitioning

\- repeatable processing

\- deterministic flight key

\- merge/upsert behavior where required

\- duplicate prevention

\- load audit records

\- source-to-target row-count reconciliation



A rerun of the same batch should not create duplicate business records.



\---



\## 7. Data Quality Requirements



The implementation must include automated or repeatable checks for:



\### Structural quality

\- required columns exist

\- expected schemas are valid

\- critical data types parse successfully



\### Completeness

\- FlightDate populated

\- Origin populated

\- Destination populated

\- Carrier populated



\### Validity

\- Cancelled values limited to valid domain

\- Diverted values limited to valid domain

\- airport codes conform to expected structure

\- delay-cause minutes cannot be negative



\### Uniqueness

\- flight business key unique after Silver processing



\### Reconciliation

\- Bronze source count documented

\- Silver accepted count documented

\- rejected/invalid count documented

\- Gold fact count reconciled with accepted Silver records



\### Weather enrichment

\- weather join coverage measured

\- missing weather observations explicitly reported



\---



\## 8. Observability Requirements



Each major pipeline execution should record:



\- run ID

\- source

\- load period

\- start timestamp

\- end timestamp

\- status

\- source row count

\- processed row count

\- rejected row count

\- target row count

\- error message when applicable



\---



\## 9. Analytics Requirements



Power BI should eventually contain at least four report pages.



\### Executive Overview

\- total flights

\- on-time arrival rate

\- average arrival delay

\- cancellation rate

\- diversion rate



\### Airport and Carrier Performance

\- airport rankings

\- carrier rankings

\- route analysis

\- delay distribution



\### Weather Impact

\- delay by weather condition

\- precipitation vs delay

\- wind vs delay

\- airport weather sensitivity



\### Data Operations

\- latest successful load

\- row counts

\- quality failures

\- weather enrichment coverage



\---



\## 10. Engineering Requirements



Repository must include:



\- public GitHub repository

\- documented architecture

\- documented project scope

\- sensible directory structure

\- configuration separated from code

\- reusable transformation logic

\- automated tests

\- GitHub Actions CI

\- clear README

\- reproducible setup instructions



Secrets, credentials, API keys, raw production-sized datasets, and environment-specific credentials must never be committed.



\---



\## 11. Definition of Done



AirOps 360 MVP is complete when:



1\. BTS flight data can be ingested into Bronze.

2\. Historical weather can be retrieved and landed in Bronze.

3\. Silver Delta tables are standardized and validated.

4\. Flight records are weather-enriched.

5\. Gold dimensional tables are produced.

6\. April-May historical load succeeds.

7\. June incremental load succeeds without duplicates.

8\. Data-quality checks execute and produce documented results.

9\. Source-to-target reconciliation is demonstrated.

10\. Fabric orchestration executes the end-to-end flow.

11\. A Direct Lake semantic model is created.

12\. A Power BI report communicates business insights.

13\. GitHub contains code, tests, architecture, documentation, and CI configuration.

14\. README explains the design and demonstrates results.



\---



\## 12. Explicit Non-Goals



The MVP will NOT include:



\- streaming architecture

\- Eventstream/Kafka

\- machine-learning delay prediction

\- real-time flight tracking

\- mobile application

\- custom production web application

\- paid aviation APIs

\- weather ingestion for every U.S. airport

\- Kubernetes

\- microservices

\- enterprise-scale multi-region deployment



These may only be considered after the defined MVP has been completed.



\---



\## 13. Change-Control Rule



Any feature not explicitly included in this file is considered out of scope unless:



1\. the MVP is already complete, or

2\. the feature replaces an existing requirement rather than expanding scope.



All material architecture or scope changes must be documented in `docs/DECISIONS.md`.



This document is the controlling scope for AirOps 360.

