-- ============================================================================
-- Analytical SQL Queries: Delhi-NCR Air Quality Analysis
-- Target Database: PostgreSQL 18 (delhi_aqi)
-- Schema: Star Schema (dim_station, dim_date, fact_daily_aqi, fact_hourly_aqi)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Executive KPI Summary
-- Business Question: What are the network-wide benchmark pollution metrics 
-- across Delhi-NCR over the 7-year monitoring window?
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(f.daily_id) AS total_station_days,
    COUNT(DISTINCT f.station_key) AS active_stations_count,
    ROUND(AVG(f.daily_mean_aqi), 2) AS network_mean_aqi,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.daily_mean_aqi)::numeric, 2) AS network_median_aqi,
    COUNT(CASE WHEN f.daily_mean_aqi > 400 THEN 1 END) AS severe_days_count,
    ROUND(
        COUNT(CASE WHEN f.daily_mean_aqi > 400 THEN 1 END) * 100.0 / COUNT(f.daily_id), 
        2
    ) AS severe_days_pct,
    ROUND(AVG(CASE WHEN d.is_winter = TRUE THEN f.daily_mean_aqi END), 2) AS winter_mean_aqi,
    ROUND(AVG(CASE WHEN d.is_winter = FALSE THEN f.daily_mean_aqi END), 2) AS non_winter_mean_aqi,
    ROUND(
        AVG(CASE WHEN d.is_winter = TRUE THEN f.daily_mean_aqi END) /
        NULLIF(AVG(CASE WHEN d.is_winter = FALSE THEN f.daily_mean_aqi END), 0),
        2
    ) AS winter_elevation_ratio
FROM fact_daily_aqi f
JOIN dim_date d ON f.calendar_date = d.calendar_date
WHERE f.is_day_valid = TRUE;


-- ----------------------------------------------------------------------------
-- Query 2: Monthly Trends & Seasonal Inversion Wave (Research Question 1)
-- Business Question: How does AQI transition month-by-month across the 7 years?
-- ----------------------------------------------------------------------------
SELECT 
    d.month,
    d.month_name,
    d.season,
    d.is_winter,
    COUNT(f.daily_id) AS monitored_station_days,
    ROUND(AVG(f.daily_mean_aqi), 2) AS mean_aqi,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.daily_mean_aqi)::numeric, 2) AS median_aqi,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY f.daily_mean_aqi)::numeric, 2) AS q1_aqi,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY f.daily_mean_aqi)::numeric, 2) AS q3_aqi,
    ROUND(
        COUNT(CASE WHEN f.daily_mean_aqi > 400 THEN 1 END) * 100.0 / COUNT(f.daily_id), 
        2
    ) AS severe_days_pct
FROM fact_daily_aqi f
JOIN dim_date d ON f.calendar_date = d.calendar_date
WHERE f.is_day_valid = TRUE
GROUP BY d.month, d.month_name, d.season, d.is_winter
ORDER BY d.month;


-- ----------------------------------------------------------------------------
-- Query 3: Station Rankings & Spatial Heterogeneity (Research Question 2)
-- Business Question: Which locations suffer the highest winter pollution burdens?
-- Uses DENSE_RANK() window function to rank stations per city and network-wide.
-- ----------------------------------------------------------------------------
WITH station_winter_stats AS (
    SELECT 
        s.city,
        s.station_name,
        s.agency,
        COUNT(f.daily_id) AS valid_winter_days,
        ROUND(AVG(f.daily_mean_aqi), 2) AS mean_winter_aqi,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.daily_mean_aqi)::numeric, 2) AS median_winter_aqi,
        ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY f.daily_mean_aqi)::numeric, 2) AS p90_winter_aqi,
        ROUND(
            COUNT(CASE WHEN f.daily_mean_aqi > 400 THEN 1 END) * 100.0 / COUNT(f.daily_id), 
            2
        ) AS severe_winter_pct
    FROM fact_daily_aqi f
    JOIN dim_station s ON f.station_key = s.station_key
    JOIN dim_date d ON f.calendar_date = d.calendar_date
    WHERE d.is_winter = TRUE AND f.is_day_valid = TRUE
    GROUP BY s.city, s.station_name, s.agency
    HAVING COUNT(f.daily_id) >= 100 -- Ensure adequate multi-year winter coverage
),
ranked_stations AS (
    SELECT 
        city,
        station_name,
        agency,
        valid_winter_days,
        median_winter_aqi,
        mean_winter_aqi,
        p90_winter_aqi,
        severe_winter_pct,
        DENSE_RANK() OVER (PARTITION BY city ORDER BY median_winter_aqi DESC) AS city_rank,
        DENSE_RANK() OVER (ORDER BY median_winter_aqi DESC) AS ncr_overall_rank
    FROM station_winter_stats
)
SELECT *
FROM ranked_stations
WHERE city_rank <= 3
ORDER BY city, city_rank;


-- ----------------------------------------------------------------------------
-- Query 4: Severity Category Distribution by Season and City (Research Question 3)
-- Business Question: How frequently do stations experience each CPCB NAQI tier?
-- ----------------------------------------------------------------------------
SELECT 
    s.city,
    d.season,
    COUNT(f.daily_id) AS total_station_days,
    COUNT(CASE WHEN f.daily_mean_aqi <= 50 THEN 1 END) AS good_count,
    COUNT(CASE WHEN f.daily_mean_aqi BETWEEN 51 AND 100 THEN 1 END) AS satisfactory_count,
    COUNT(CASE WHEN f.daily_mean_aqi BETWEEN 101 AND 200 THEN 1 END) AS moderate_count,
    COUNT(CASE WHEN f.daily_mean_aqi BETWEEN 201 AND 300 THEN 1 END) AS poor_count,
    COUNT(CASE WHEN f.daily_mean_aqi BETWEEN 301 AND 400 THEN 1 END) AS very_poor_count,
    COUNT(CASE WHEN f.daily_mean_aqi > 400 THEN 1 END) AS severe_count,
    ROUND(
        COUNT(CASE WHEN f.daily_mean_aqi > 400 THEN 1 END) * 100.0 / COUNT(f.daily_id), 
        2
    ) AS severe_pct
FROM fact_daily_aqi f
JOIN dim_station s ON f.station_key = s.station_key
JOIN dim_date d ON f.calendar_date = d.calendar_date
WHERE f.is_day_valid = TRUE
GROUP BY s.city, d.season
ORDER BY s.city, severe_pct DESC;


-- ----------------------------------------------------------------------------
-- Query 5: Diurnal Diurnal Profiling (Research Question 6)
-- Business Question: What is the 24-hour diurnal profile of AQI in Winter vs Monsoon?
-- Evaluates boundary layer mixing height vs morning rush hour dynamics.
-- ----------------------------------------------------------------------------
SELECT 
    d.season,
    h.hour,
    COUNT(h.observation_id) AS valid_observations,
    ROUND(AVG(h.aqi_cleaned), 2) AS mean_hourly_aqi,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY h.aqi_cleaned)::numeric, 2) AS median_hourly_aqi
FROM fact_hourly_aqi h
JOIN dim_date d ON h.calendar_date = d.calendar_date
WHERE h.is_valid = TRUE AND d.season IN ('Winter', 'Monsoon')
GROUP BY d.season, h.hour
ORDER BY d.season, h.hour;


-- ----------------------------------------------------------------------------
-- Query 6: Diwali Event-Study Trajectory (Research Question 8)
-- Business Question: How does AQI surge and dissipate around Diwali across the 7 years?
-- Uses rolling window centered on festival day (t-7 to t+7).
-- ----------------------------------------------------------------------------
WITH diwali_daily AS (
    SELECT 
        d.year,
        d.calendar_date,
        d.diwali_relative_day,
        ROUND(AVG(f.daily_mean_aqi), 2) AS network_mean_aqi,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.daily_mean_aqi)::numeric, 2) AS network_median_aqi
    FROM fact_daily_aqi f
    JOIN dim_date d ON f.calendar_date = d.calendar_date
    WHERE d.is_diwali_window = TRUE AND f.is_day_valid = TRUE
    GROUP BY d.year, d.calendar_date, d.diwali_relative_day
)
SELECT 
    year,
    calendar_date,
    diwali_relative_day,
    network_median_aqi,
    network_mean_aqi,
    ROUND(
        AVG(network_median_aqi) OVER (
            PARTITION BY year 
            ORDER BY diwali_relative_day 
            ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
        ), 2
    ) AS smoothed_3day_median_aqi
FROM diwali_daily
ORDER BY year, diwali_relative_day;


-- ----------------------------------------------------------------------------
-- Query 7: Station Completeness & Sensor Capping Audit (Research Question 7)
-- Business Question: Are dirtier stations subject to more downtime or capping?
-- ----------------------------------------------------------------------------
SELECT 
    s.city,
    s.station_name,
    s.agency,
    s.total_recorded_days,
    s.uptime_hourly_pct,
    s.temporal_coverage_pct,
    s.capped_hours_pct,
    s.mean_aqi,
    s.median_aqi
FROM dim_station s
ORDER BY s.capped_hours_pct DESC, s.median_aqi DESC
LIMIT 15;
