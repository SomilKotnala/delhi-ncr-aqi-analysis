# Data Dictionary & Schema Specification

## 1. Official CPCB Air Quality Index (AQI) Categorization

The National Air Quality Index (NAQI) established by the Central Pollution Control Board (CPCB) and Ministry of Environment, Forest and Climate Change (MoEFCC) groups ambient air quality into six categories based on health impact:

| AQI Range | Category | Color Representation | Hex Code | Official Associated Health Impact |
| :---: | :---: | :---: | :---: | :--- |
| **0 – 50** | **Good** | Dark Green | `#009639` | Minimal health impact. |
| **51 – 100** | **Satisfactory** | Light Green | `#7ec242` | Minor breathing discomfort to sensitive people. |
| **101 – 200** | **Moderate** | Yellow | `#fdd023` | Breathing discomfort to people with lungs, asthma and heart diseases. |
| **201 – 300** | **Poor** | Orange | `#f58220` | Breathing discomfort to most people on prolonged exposure. |
| **301 – 400** | **Very Poor** | Red | `#e62b1e` | Respiratory illness on prolonged exposure. Pronounced effect on people with lung/heart disease. |
| **401 – 500** | **Severe** | Maroon | `#9b111e` | Affects healthy people and seriously impacts those with existing diseases. |
| **> 500** | **Extreme / Sensor Cap** | Dark Purple | `#4a0e4e` | Hazardous episode; values > 500 represent sensor saturation or instrument anomaly. |

---

## 2. Raw Ingestion Schema (`data/raw/cpcb-aqi.parquet`)

The raw file represents station-day records in wide format with 24 individual hourly observation columns:

| Column Name | Source Type | Storage Type | Nullable | Example / Description |
| :--- | :--- | :--- | :---: | :--- |
| `Station ID` | String | UTF-8 String | No | Upstream folder identifier (Note: duplicated across city stations in raw repo). |
| `State` | String | UTF-8 String | No | State or Union Territory name (e.g., `Delhi`, `Haryana`, `Uttar Pradesh`). |
| `City` | String | UTF-8 String | No | Monitored city name (e.g., `Delhi`, `Faridabad`, `Gurugram`, `Ghaziabad`, `Noida`). |
| `Station Name` | String | UTF-8 String | No | Unique descriptive name (e.g., `Anand Vihar Delhi DPCC`, `Sector 62 Noida IMD`). |
| `Date` | Timestamp | `datetime64[ns]` | No | Calendar observation date (`2017-01-01 00:00:00` to `2023-12-31 00:00:00`). |
| `00:00:00` to `23:00:00` | Integer | `Int64` (nullable) | Yes | 24 columns recording hourly AQI readings (1–500; null if sensor offline). |

---

## 3. Processed Hourly Analytical Schema (`fact_hourly_aqi`)

Standardized long/tidy format suitable for relational database loading, time-series analysis, and Power BI time intelligence:

| Column Name | Target SQL Type | Pandas Dtype | Constraints / Rules | Description |
| :--- | :--- | :--- | :--- | :--- |
| `station_key` | `VARCHAR(32)` | `string` | Foreign Key to `dim_station` | Standardized slugified station key (e.g., `delhi_anand_vihar`). |
| `timestamp_ist` | `TIMESTAMP` | `datetime64[ns]` | Not Null | Observation timestamp in Indian Standard Time (UTC+05:30). |
| `date` | `DATE` | `datetime64[ns]` | Not Null | Observation date (`YYYY-MM-DD`). |
| `year` | `SMALLINT` | `int16` | 2017 to 2023 | Calendar year. |
| `month` | `SMALLINT` | `int8` | 1 to 12 | Month of the year. |
| `day_of_week` | `SMALLINT` | `int8` | 0 (Monday) to 6 (Sunday) | Day index. |
| `hour` | `SMALLINT` | `int8` | 0 to 23 | Hour of day (0 to 23). |
| `aqi_value` | `NUMERIC(6,2)` | `float32` | $1.00 \le \text{AQI} \le 500.00$ | Cleaned hourly AQI measurement. |
| `aqi_category` | `VARCHAR(16)` | `category` | Valid CPCB category | Good, Satisfactory, Moderate, Poor, Very Poor, Severe. |
| `is_sensor_capped`| `BOOLEAN` | `bool` | True if $\text{AQI} = 500$ | Flag indicating CPCB mathematical formula reporting ceiling (500.0). |
| `is_anomalous` | `BOOLEAN` | `bool` | True if $\text{AQI} > 500$ | Instrument/telemetry calibration anomaly flag (10 records in 2.44M). |

---

## 4. Processed Daily Aggregated Schema (`fact_daily_aqi`)

Aggregated station-day analytical table preventing pseudoreplication:

| Column Name | Target SQL Type | Description |
| :--- | :--- | :--- |
| `station_key` | `VARCHAR(32)` | Reference to monitoring station. |
| `date` | `DATE` | Observation date. |
| `valid_hours_count` | `SMALLINT` | Count of valid non-null hourly readings recorded ($0 \le N \le 24$). |
| `is_day_valid` | `BOOLEAN` | True if `valid_hours_count` $\ge 16$ (CPCB $67\%$ completeness standard). |
| `daily_mean_aqi` | `NUMERIC(6,2)` | Arithmetic mean of valid hourly readings. |
| `daily_median_aqi` | `NUMERIC(6,2)` | Median of valid hourly readings (robust to intraday spikes). |
| `daily_min_aqi` | `NUMERIC(6,2)` | Minimum hourly reading of the day. |
| `daily_max_aqi` | `NUMERIC(6,2)` | Peak hourly reading of the day. |
| `daily_aqi_category`| `VARCHAR(16)` | Category assigned based on daily mean AQI. |
| `season` | `VARCHAR(16)` | Winter (Nov-Jan), Pre-Monsoon (Feb-May), Monsoon (Jun-Sep), Post-Monsoon (Oct). |
| `is_winter` | `BOOLEAN` | True if month $\in \{11, 12, 1\}$. |
| `is_diwali_window` | `BOOLEAN` | True if within $\pm 7$ days of Diwali day for the given year. |

---

## 5. Station Dimension Schema (`dim_station`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `station_key` | `VARCHAR(32) PRIMARY KEY` | Standardized unique station identifier. |
| `station_name` | `VARCHAR(128)` | Official full station name. |
| `city` | `VARCHAR(64)` | City name (Delhi, Gurugram, Faridabad, Ghaziabad, Noida). |
| `state` | `VARCHAR(64)` | State / UT (Delhi, Haryana, Uttar Pradesh). |
| `agency` | `VARCHAR(32)` | Operating authority extracted from name (DPCC, CPCB, IMD, HSPCB, UPPCB, IITM). |
| `first_record_date` | `DATE` | Date of earliest available measurement in dataset. |
| `last_record_date` | `DATE` | Date of latest available measurement in dataset. |
| `total_recorded_days`| `INTEGER` | Count of days with at least one record. |
| `coverage_percentage`| `NUMERIC(5,2)` | Percentage of days active out of 2,556 possible days. |
