# AirOps 360 - Gold Release v0.1

## Release gate

Same-batch rerun: PASS

- Fact rows: 597,919
- Distinct flight_key: 597,919
- Duplicate fact business-key groups: 0
- Daily airport aggregate rows: 10,031
- Duplicate airport-day groups: 0

Publication timestamps are intentionally excluded from the
stable rerun signature because they change on every publication.

## KPI reconciliation

Gold KPIs were independently reconciled to
`lh_airops_silver.slv_flights_weather_enriched`.

- Total Flights: 597,919
- Cancellation Rate: 0.9035%
  (5,402 / 597,919)
- Arrival Delay >=15 Rate: 20.1989%
  (119,417 /
  591,206)
- Unknown arrival-delay outcomes excluded: 6,713

## Scope

Weather remains an ORD/ATL April 2026 pilot.
NULL weather outside pilot coverage means weather data is unavailable,
not that weather was good.

This release demonstrates rerun safety, business-grain integrity,
and Silver-to-Gold KPI reconciliation.
