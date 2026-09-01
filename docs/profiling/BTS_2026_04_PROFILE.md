# BTS April 2026 Source Profile v0.1

**Generated:** 2026-09-01 20:49:50 UTC

**Dataset:** Reporting Carrier On-Time Performance

**Source period:** April 2026

**Purpose:** Validate AirOps 360 Data Contract v0.1 against the actual BTS April 2026 source before Bronze/Silver implementation.

## 1. Source summary

| Metric | Observed |
| --- | --- |
| Source row count | 597,919 |
| Source column count | 110 |
| Minimum FlightDate | 2026-04-01 |
| Maximum FlightDate | 2026-04-30 |
| FlightDate parse failures | 0 |
| Rows outside April 2026 | 0 |

## 2. Required contract fields

Required fields expected: **20**

Required fields present: **20**

Required fields missing: **0**

**Result: all required AirOps 360 v0.1 BTS fields are present.**

## 3. Candidate business-key profile

Candidate key:

```text
FlightDate
Reporting_Airline
Flight_Number_Reporting_Airline
Origin
Dest
CRSDepTime
```

| Metric | Observed |
| --- | --- |
| Total source rows | 597,919 |
| Rows with null candidate-key component | 0 |
| Rows with complete candidate key | 597,919 |
| Distinct complete candidate keys | 597,919 |
| Rows involved in duplicate candidate keys | 0 |
| Duplicate candidate-key groups | 0 |
| Complete-key uniqueness | 100.000000% |

### Candidate-key component nulls

| Field | Null count | Null % |
| --- | --- | --- |
| FlightDate | 0 | 0.0000% |
| Reporting_Airline | 0 | 0.0000% |
| Flight_Number_Reporting_Airline | 0 | 0.0000% |
| Origin | 0 | 0.0000% |
| Dest | 0 | 0.0000% |
| CRSDepTime | 0 | 0.0000% |

**Observed result: the provisional candidate business key is unique for the April 2026 source extract.**

## 4. Top origin airports

| Rank | Origin | Flights | Share of source |
| --- | --- | --- | --- |
| 1 | ORD | 33,206 | 5.55% |
| 2 | ATL | 26,607 | 4.45% |
| 3 | DFW | 25,686 | 4.30% |
| 4 | DEN | 25,345 | 4.24% |
| 5 | PHX | 17,679 | 2.96% |
| 6 | LAX | 15,732 | 2.63% |
| 7 | CLT | 15,396 | 2.57% |
| 8 | LAS | 14,672 | 2.45% |
| 9 | MCO | 14,604 | 2.44% |
| 10 | SEA | 12,864 | 2.15% |
| 11 | BOS | 12,626 | 2.11% |
| 12 | SFO | 12,401 | 2.07% |
| 13 | DCA | 11,802 | 1.97% |
| 14 | LGA | 11,443 | 1.91% |
| 15 | DTW | 10,417 | 1.74% |
| 16 | EWR | 10,358 | 1.73% |
| 17 | IAH | 10,022 | 1.68% |
| 18 | SLC | 9,877 | 1.65% |
| 19 | MSP | 9,639 | 1.61% |
| 20 | BNA | 9,617 | 1.61% |

> The top-airport ranking is profiling evidence. The final AirOps weather-airport scope should be frozen only after this evidence is reviewed.

## 5. Cancelled / Diverted observed domains

### Cancelled

| Value | Row count |
| --- | --- |
| 0.0 | 592,517 |
| 1.0 | 5,402 |

### Diverted

| Value | Row count |
| --- | --- |
| 0.0 | 596,608 |
| 1.0 | 1,311 |

## 6. Full schema and null profile

> `Observed dtype` is pandas source inference, not the final AirOps Silver logical type.

| Column | Observed dtype | Null count | Null % |
| --- | --- | --- | --- |
| Year | int64 | 0 | 0.00% |
| Quarter | int64 | 0 | 0.00% |
| Month | int64 | 0 | 0.00% |
| DayofMonth | int64 | 0 | 0.00% |
| DayOfWeek | int64 | 0 | 0.00% |
| FlightDate | str | 0 | 0.00% |
| Reporting_Airline | str | 0 | 0.00% |
| DOT_ID_Reporting_Airline | int64 | 0 | 0.00% |
| IATA_CODE_Reporting_Airline | str | 0 | 0.00% |
| Tail_Number | str | 617 | 0.10% |
| Flight_Number_Reporting_Airline | int64 | 0 | 0.00% |
| OriginAirportID | int64 | 0 | 0.00% |
| OriginAirportSeqID | int64 | 0 | 0.00% |
| OriginCityMarketID | int64 | 0 | 0.00% |
| Origin | str | 0 | 0.00% |
| OriginCityName | str | 0 | 0.00% |
| OriginState | str | 0 | 0.00% |
| OriginStateFips | int64 | 0 | 0.00% |
| OriginStateName | str | 0 | 0.00% |
| OriginWac | int64 | 0 | 0.00% |
| DestAirportID | int64 | 0 | 0.00% |
| DestAirportSeqID | int64 | 0 | 0.00% |
| DestCityMarketID | int64 | 0 | 0.00% |
| Dest | str | 0 | 0.00% |
| DestCityName | str | 0 | 0.00% |
| DestState | str | 0 | 0.00% |
| DestStateFips | int64 | 0 | 0.00% |
| DestStateName | str | 0 | 0.00% |
| DestWac | int64 | 0 | 0.00% |
| CRSDepTime | int64 | 0 | 0.00% |
| DepTime | float64 | 5,115 | 0.86% |
| DepDelay | float64 | 5,171 | 0.86% |
| DepDelayMinutes | float64 | 5,171 | 0.86% |
| DepDel15 | float64 | 5,171 | 0.86% |
| DepartureDelayGroups | float64 | 5,171 | 0.86% |
| DepTimeBlk | str | 0 | 0.00% |
| TaxiOut | float64 | 5,357 | 0.90% |
| WheelsOff | float64 | 5,357 | 0.90% |
| WheelsOn | float64 | 5,545 | 0.93% |
| TaxiIn | float64 | 5,545 | 0.93% |
| CRSArrTime | int64 | 0 | 0.00% |
| ArrTime | float64 | 5,545 | 0.93% |
| ArrDelay | float64 | 6,713 | 1.12% |
| ArrDelayMinutes | float64 | 6,713 | 1.12% |
| ArrDel15 | float64 | 6,713 | 1.12% |
| ArrivalDelayGroups | float64 | 6,713 | 1.12% |
| ArrTimeBlk | str | 0 | 0.00% |
| Cancelled | float64 | 0 | 0.00% |
| CancellationCode | str | 592,517 | 99.10% |
| Diverted | float64 | 0 | 0.00% |
| CRSElapsedTime | float64 | 0 | 0.00% |
| ActualElapsedTime | float64 | 6,713 | 1.12% |
| AirTime | float64 | 6,713 | 1.12% |
| Flights | float64 | 0 | 0.00% |
| Distance | float64 | 0 | 0.00% |
| DistanceGroup | int64 | 0 | 0.00% |
| CarrierDelay | float64 | 478,502 | 80.03% |
| WeatherDelay | float64 | 478,502 | 80.03% |
| NASDelay | float64 | 478,502 | 80.03% |
| SecurityDelay | float64 | 478,502 | 80.03% |
| LateAircraftDelay | float64 | 478,502 | 80.03% |
| FirstDepTime | float64 | 593,998 | 99.34% |
| TotalAddGTime | float64 | 594,003 | 99.35% |
| LongestAddGTime | float64 | 594,003 | 99.35% |
| DivAirportLandings | int64 | 0 | 0.00% |
| DivReachedDest | float64 | 596,608 | 99.78% |
| DivActualElapsedTime | float64 | 596,751 | 99.80% |
| DivArrDelay | float64 | 596,751 | 99.80% |
| DivDistance | float64 | 596,608 | 99.78% |
| Div1Airport | str | 596,543 | 99.77% |
| Div1AirportID | float64 | 596,543 | 99.77% |
| Div1AirportSeqID | float64 | 596,543 | 99.77% |
| Div1WheelsOn | float64 | 596,543 | 99.77% |
| Div1TotalGTime | float64 | 596,543 | 99.77% |
| Div1LongestGTime | float64 | 596,543 | 99.77% |
| Div1WheelsOff | float64 | 596,726 | 99.80% |
| Div1TailNum | str | 596,726 | 99.80% |
| Div2Airport | str | 597,911 | 100.00% |
| Div2AirportID | float64 | 597,911 | 100.00% |
| Div2AirportSeqID | float64 | 597,911 | 100.00% |
| Div2WheelsOn | float64 | 597,911 | 100.00% |
| Div2TotalGTime | float64 | 597,911 | 100.00% |
| Div2LongestGTime | float64 | 597,911 | 100.00% |
| Div2WheelsOff | float64 | 597,916 | 100.00% |
| Div2TailNum | str | 597,916 | 100.00% |
| Div3Airport | float64 | 597,919 | 100.00% |
| Div3AirportID | float64 | 597,919 | 100.00% |
| Div3AirportSeqID | float64 | 597,919 | 100.00% |
| Div3WheelsOn | float64 | 597,919 | 100.00% |
| Div3TotalGTime | float64 | 597,919 | 100.00% |
| Div3LongestGTime | float64 | 597,919 | 100.00% |
| Div3WheelsOff | float64 | 597,919 | 100.00% |
| Div3TailNum | float64 | 597,919 | 100.00% |
| Div4Airport | float64 | 597,919 | 100.00% |
| Div4AirportID | float64 | 597,919 | 100.00% |
| Div4AirportSeqID | float64 | 597,919 | 100.00% |
| Div4WheelsOn | float64 | 597,919 | 100.00% |
| Div4TotalGTime | float64 | 597,919 | 100.00% |
| Div4LongestGTime | float64 | 597,919 | 100.00% |
| Div4WheelsOff | float64 | 597,919 | 100.00% |
| Div4TailNum | float64 | 597,919 | 100.00% |
| Div5Airport | float64 | 597,919 | 100.00% |
| Div5AirportID | float64 | 597,919 | 100.00% |
| Div5AirportSeqID | float64 | 597,919 | 100.00% |
| Div5WheelsOn | float64 | 597,919 | 100.00% |
| Div5TotalGTime | float64 | 597,919 | 100.00% |
| Div5LongestGTime | float64 | 597,919 | 100.00% |
| Div5WheelsOff | float64 | 597,919 | 100.00% |
| Div5TailNum | float64 | 597,919 | 100.00% |
| Unnamed: 109 | float64 | 597,919 | 100.00% |

## 7. Contract decision

This document records source-profiling evidence only.

No AirOps 360 data-contract assumption should be changed silently as part of profiling.

If source grain, required-field presence, candidate-key uniqueness, or domain behavior differs from Data Contract v0.1, the discrepancy must be reviewed and documented before implementation changes are made.