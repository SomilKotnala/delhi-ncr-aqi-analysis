-- ============================================================================
-- Relational Star Schema DDL: Delhi-NCR Air Quality Analysis
-- Target Engine: PostgreSQL 14+ (Tested on PostgreSQL 18.4)
-- Database: delhi_aqi (Tablespace: aqi_tablespace on D: drive)
-- ============================================================================

-- Drop tables in reverse foreign key order if re-creating
DROP TABLE IF EXISTS fact_hourly_aqi CASCADE;
DROP TABLE IF EXISTS fact_daily_aqi CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_station CASCADE;

-- ----------------------------------------------------------------------------
-- 1. Station Dimension Table (dim_station)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_station (
    station_key             VARCHAR(64) PRIMARY KEY,
    raw_station_id          VARCHAR(32) NOT NULL,
    station_name            VARCHAR(128) NOT NULL,
    city                    VARCHAR(64) NOT NULL,
    state                   VARCHAR(64) NOT NULL,
    agency                  VARCHAR(32) NOT NULL,
    first_record_date       DATE NOT NULL,
    last_record_date        DATE NOT NULL,
    total_recorded_days     INTEGER NOT NULL,
    total_hourly_records    INTEGER NOT NULL,
    valid_hourly_records    INTEGER NOT NULL,
    missing_hourly_records  INTEGER NOT NULL,
    uptime_hourly_pct       NUMERIC(5,2) NOT NULL,
    temporal_coverage_pct   NUMERIC(5,2) NOT NULL,
    capped_hours_pct        NUMERIC(5,2) NOT NULL,
    mean_aqi                NUMERIC(6,2),
    median_aqi              NUMERIC(6,2),
    created_at              TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
) TABLESPACE aqi_tablespace;

COMMENT ON TABLE dim_station IS 'Dimension table containing metadata, location, operating agency, and uptime coverage for 56 CAAQMS stations in Delhi-NCR.';
COMMENT ON COLUMN dim_station.station_key IS 'Surrogate primary key resolving upstream station ID duplication across cities.';

-- ----------------------------------------------------------------------------
-- 2. Date Dimension Table (dim_date)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_date (
    calendar_date       DATE PRIMARY KEY,
    year                SMALLINT NOT NULL,
    month               SMALLINT NOT NULL,
    month_name          VARCHAR(16) NOT NULL,
    day                 SMALLINT NOT NULL,
    day_of_week         SMALLINT NOT NULL, -- 0 = Monday, 6 = Sunday
    day_name            VARCHAR(16) NOT NULL,
    is_weekend          BOOLEAN NOT NULL,
    season              VARCHAR(32) NOT NULL,
    is_winter           BOOLEAN NOT NULL,
    is_diwali_window    BOOLEAN NOT NULL,
    diwali_relative_day SMALLINT           -- -7 to +7 relative to annual festival date, NULL otherwise
) TABLESPACE aqi_tablespace;

COMMENT ON TABLE dim_date IS 'Pre-computed calendar dimension for time intelligence, seasonal partitioning, and Diwali event studies.';

-- ----------------------------------------------------------------------------
-- 3. Daily Aggregated Fact Table (fact_daily_aqi)
-- ----------------------------------------------------------------------------
CREATE TABLE fact_daily_aqi (
    daily_id                BIGSERIAL PRIMARY KEY,
    station_key             VARCHAR(64) NOT NULL REFERENCES dim_station(station_key) ON DELETE CASCADE,
    calendar_date           DATE NOT NULL REFERENCES dim_date(calendar_date) ON DELETE CASCADE,
    total_hours             SMALLINT NOT NULL DEFAULT 24,
    valid_hours_count       SMALLINT NOT NULL,
    missing_hours_count     SMALLINT NOT NULL,
    capped_hours_count      SMALLINT NOT NULL,
    anomalous_hours_count   SMALLINT NOT NULL,
    is_day_valid            BOOLEAN NOT NULL, -- True if valid_hours_count >= 16 (CPCB 67% rule)
    daily_mean_aqi          NUMERIC(6,2),
    daily_median_aqi        NUMERIC(6,2),
    daily_min_aqi           NUMERIC(6,2),
    daily_max_aqi           NUMERIC(6,2),
    daily_category          VARCHAR(32),
    season                  VARCHAR(32),
    is_winter               BOOLEAN,
    is_diwali_window        BOOLEAN,
    diwali_relative_day     SMALLINT,
    CONSTRAINT uq_daily_station_date UNIQUE (station_key, calendar_date)
) TABLESPACE aqi_tablespace;

COMMENT ON TABLE fact_daily_aqi IS 'Daily station-level aggregated fact table designed to avoid pseudoreplication in inferential testing.';

-- ----------------------------------------------------------------------------
-- 4. Hourly Fact Table (fact_hourly_aqi)
-- ----------------------------------------------------------------------------
CREATE TABLE fact_hourly_aqi (
    observation_id          BIGSERIAL PRIMARY KEY,
    station_key             VARCHAR(64) NOT NULL REFERENCES dim_station(station_key) ON DELETE CASCADE,
    calendar_date           DATE NOT NULL REFERENCES dim_date(calendar_date) ON DELETE CASCADE,
    timestamp_ist           TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    timestamp_utc           TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    hour                    SMALLINT NOT NULL CHECK (hour BETWEEN 0 AND 23),
    aqi_raw                 NUMERIC(7,2),
    aqi_cleaned             NUMERIC(7,2),
    aqi_category            VARCHAR(32),
    is_missing              BOOLEAN NOT NULL,
    is_sensor_capped        BOOLEAN NOT NULL, -- True if aqi_raw == 500 (reporting ceiling)
    is_anomalous            BOOLEAN NOT NULL, -- True if aqi_raw > 500 or <= 0
    is_valid                BOOLEAN NOT NULL,
    CONSTRAINT uq_hourly_station_timestamp UNIQUE (station_key, timestamp_ist)
) TABLESPACE aqi_tablespace;

COMMENT ON TABLE fact_hourly_aqi IS 'Granular hourly fact table containing 2.66M records with full anomaly flags and dual timestamps.';

-- ----------------------------------------------------------------------------
-- 5. Strategic Indexes for Analytical Performance (Stored on D: Drive)
-- ----------------------------------------------------------------------------
CREATE INDEX idx_station_city ON dim_station(city) TABLESPACE aqi_tablespace;
CREATE INDEX idx_station_agency ON dim_station(agency) TABLESPACE aqi_tablespace;

CREATE INDEX idx_date_year_month ON dim_date(year, month) TABLESPACE aqi_tablespace;
CREATE INDEX idx_date_is_winter ON dim_date(is_winter) TABLESPACE aqi_tablespace;
CREATE INDEX idx_date_is_diwali ON dim_date(is_diwali_window) TABLESPACE aqi_tablespace;

CREATE INDEX idx_daily_station_key ON fact_daily_aqi(station_key) TABLESPACE aqi_tablespace;
CREATE INDEX idx_daily_date ON fact_daily_aqi(calendar_date) TABLESPACE aqi_tablespace;
CREATE INDEX idx_daily_is_winter ON fact_daily_aqi(is_winter) TABLESPACE aqi_tablespace;
CREATE INDEX idx_daily_is_day_valid ON fact_daily_aqi(is_day_valid) TABLESPACE aqi_tablespace;

CREATE INDEX idx_hourly_station_key ON fact_hourly_aqi(station_key) TABLESPACE aqi_tablespace;
CREATE INDEX idx_hourly_timestamp_ist ON fact_hourly_aqi(timestamp_ist) TABLESPACE aqi_tablespace;
CREATE INDEX idx_hourly_calendar_date ON fact_hourly_aqi(calendar_date) TABLESPACE aqi_tablespace;
CREATE INDEX idx_hourly_hour ON fact_hourly_aqi(hour) TABLESPACE aqi_tablespace;
CREATE INDEX idx_hourly_is_valid ON fact_hourly_aqi(is_valid) TABLESPACE aqi_tablespace;
