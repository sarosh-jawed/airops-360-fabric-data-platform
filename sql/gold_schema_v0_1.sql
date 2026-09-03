/*
AirOps 360
Gold Star Schema v0.1

Logical DDL draft.

This file defines intended Gold table shapes and types.
Physical Delta implementation may be adjusted when the Silver
implementation establishes final Spark/Fabric data types.

Relationships shown here are logical modeling relationships.
*/

-- ============================================================
-- DIM_DATE
-- Grain: one calendar date
-- ============================================================

CREATE TABLE dim_date (
    date_key            INT           NOT NULL,
    flight_date         DATE          NOT NULL,
    year                SMALLINT      NOT NULL,
    quarter             TINYINT       NOT NULL,
    month               TINYINT       NOT NULL,
    day_of_month        TINYINT       NOT NULL,
    day_of_week         TINYINT       NOT NULL,
    day_name            VARCHAR(20)   NOT NULL
);


-- ============================================================
-- DIM_AIRPORT
-- Grain: one distinct BTS airport code
--
-- Same dimension is role-played by:
--   origin_airport_key
--   destination_airport_key
--
-- Weather metadata is nullable for airports outside the
-- controlled Open-Meteo scope.
-- ============================================================

CREATE TABLE dim_airport (
    airport_key         BIGINT         NOT NULL,
    airport_code        VARCHAR(3)     NOT NULL,
    airport_name        VARCHAR(200)   NULL,
    latitude            DECIMAL(9,6)   NULL,
    longitude           DECIMAL(9,6)   NULL,
    timezone_iana       VARCHAR(100)   NULL,
    weather_scope_rank  INT            NULL,
    weather_scope_flag  BOOLEAN        NOT NULL,
    active_flag         BOOLEAN        NULL
);


-- ============================================================
-- DIM_CARRIER
-- Grain: one Reporting_Airline carrier code
--
-- Carrier name is intentionally omitted until an authoritative
-- lookup source is introduced.
-- ============================================================

CREATE TABLE dim_carrier (
    carrier_key         BIGINT        NOT NULL,
    carrier_code        VARCHAR(10)   NOT NULL
);


-- ============================================================
-- FACT_FLIGHT_PERFORMANCE
-- Grain: one scheduled carrier flight occurrence
-- ============================================================

CREATE TABLE fact_flight_performance (
    flight_key                       VARCHAR(64)    NOT NULL,

    date_key                         INT            NOT NULL,
    origin_airport_key               BIGINT         NOT NULL,
    destination_airport_key          BIGINT         NOT NULL,
    carrier_key                      BIGINT         NOT NULL,

    flight_number                    VARCHAR(20)    NOT NULL,

    crs_departure_time               VARCHAR(4)     NOT NULL,
    actual_departure_time            VARCHAR(4)     NULL,
    crs_arrival_time                 VARCHAR(4)     NOT NULL,
    actual_arrival_time              VARCHAR(4)     NULL,

    departure_delay_minutes          DECIMAL(10,2)  NULL,
    arrival_delay_minutes            DECIMAL(10,2)  NULL,

    cancelled_flag                   BOOLEAN        NOT NULL,
    diverted_flag                    BOOLEAN        NOT NULL,

    air_time_minutes                 DECIMAL(10,2)  NULL,
    distance                         DECIMAL(10,2)  NULL,

    carrier_delay_minutes            DECIMAL(10,2)  NULL,
    weather_delay_minutes            DECIMAL(10,2)  NULL,
    nas_delay_minutes                DECIMAL(10,2)  NULL,
    security_delay_minutes           DECIMAL(10,2)  NULL,
    late_aircraft_delay_minutes      DECIMAL(10,2)  NULL,

    origin_weather_hour_local        TIMESTAMP      NULL,
    origin_temperature_2m            DECIMAL(10,2)  NULL,
    origin_precipitation             DECIMAL(10,2)  NULL,
    origin_rain                      DECIMAL(10,2)  NULL,
    origin_snowfall                  DECIMAL(10,2)  NULL,
    origin_weather_code              INT            NULL,
    origin_wind_speed_10m            DECIMAL(10,2)  NULL,
    origin_wind_gusts_10m            DECIMAL(10,2)  NULL,
    weather_match_flag               BOOLEAN        NOT NULL,

    load_run_id                      VARCHAR(100)   NOT NULL
);


-- ============================================================
-- OPS_LOAD_AUDIT
-- Grain: one pipeline run + source/batch execution
-- ============================================================

CREATE TABLE ops_load_audit (
    run_id                   VARCHAR(100)    NOT NULL,
    source_name              VARCHAR(100)    NOT NULL,
    batch_key                VARCHAR(250)    NOT NULL,

    load_year                SMALLINT        NOT NULL,
    load_month               TINYINT         NOT NULL,
    contract_version         VARCHAR(20)     NOT NULL,

    start_timestamp_utc      TIMESTAMP       NOT NULL,
    end_timestamp_utc        TIMESTAMP       NULL,

    status                   VARCHAR(20)     NOT NULL,

    source_row_count         BIGINT          NULL,
    processed_row_count      BIGINT          NULL,
    rejected_row_count       BIGINT          NULL,
    duplicate_row_count      BIGINT          NULL,

    weather_match_count      BIGINT          NULL,
    weather_unmatched_count  BIGINT          NULL,

    target_row_count         BIGINT          NULL,

    error_message            VARCHAR(4000)   NULL
);


/*
Logical relationships

dim_date.date_key
    -> fact_flight_performance.date_key

dim_airport.airport_key
    -> fact_flight_performance.origin_airport_key

dim_airport.airport_key
    -> fact_flight_performance.destination_airport_key

dim_carrier.carrier_key
    -> fact_flight_performance.carrier_key

The deterministic flight_key is retained as the flight-record identity
for deduplication, merge/upsert, idempotency, and lineage.
*/