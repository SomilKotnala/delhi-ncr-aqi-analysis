# Data Quality & Cleaning Audit Report: Delhi-NCR Air Quality (2017–2023)

**Generated:** 2026-10-22 16:14:16  
**Data Authority:** Central Pollution Control Board (CPCB), MoEFCC, Govt. of India  
**Upstream Repository:** `Vonter/india-cpcb-aqi` (ODbL 1.0)  

---

## 1. Executive Summary & Transformation Audit

| Metric | Before Cleaning (Raw) | After Cleaning (Processed) | Notes |
| :--- | :--- | :--- | :--- |
| **Geographic Scope** | All India (248 cities) | **Delhi-NCR (5 cities)** | Filtered: Delhi, Gurugram, Faridabad, Ghaziabad, Noida |
| **Input Station-Days** | 562,878 rows | **111,014 rows** | 100% of Delhi-NCR station-days preserved; 0 dropped |
| **Format** | Wide (24 hourly columns) | **Tidy Long (Station-Hour)** | 1 row per station per hour |
| **Total Hourly Records**| N/A | **2,664,336 records** | Exactly $111,014 \times 24$ station-hours |
| **Valid Hourly Records**| Unverified | **2,441,802 records (91.65%)** | Complete, non-anomalous measurements |
| **Missing Hours** | Unverified | **222,534 records (8.35%)** | Station downtime or sensor offline |
| **Unique Station IDs** | 5 (Duplicated upstream) | **56 Unique Surrogate Keys** | Distinct stations mapped via slugified surrogate keys |
| **Monitored Cities** | 248 | **5 cities** | Delhi (39), Faridabad (4), Gurugram (4), Ghaziabad (3), Noida (6) |
| **Date Range** | 2017-01-01 to 2023-12-31 | **2017-01-01 to 2023-12-31** | **7 full calendar years** (2,556 consecutive days) |

---

## 2. Source Timezone Verification & Findings

### Evidence of Indian Standard Time (IST, UTC+05:30)
1. **Institutional Evidence**: Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by CPCB and state boards publish regulatory bulletins in Indian Standard Time (IST). The official CPCB 4:00 PM bulletin aggregates the prior 24 hours of local measurements.
2. **Atmospheric Diurnal Evidence**: Diurnal profiling of the raw hourly columns (`00:00:00` to `23:00:00`) across all 111,014 records reveals:
   - **Morning Rush Rise**: AQI begins rising at `07:00:00` (217.7) and peaks during morning traffic at `09:00:00`–`10:00:00` (234.9).
   - **Solar Dispersion Minimum**: AQI reaches its diurnal minimum between `15:00:00` and `17:00:00` (168.6), directly matching maximum solar heating and vertical boundary-layer mixing height.
   - **Nocturnal Inversion Peak**: AQI climbs sharply after sunset (`18:00:00` onwards), peaking at night between `22:00:00` and `00:00:00` (242.6) due to nocturnal boundary-layer compression.
   - If the columns were UTC, `17:00:00` would correspond to 10:30 PM IST (late night), which contradicts established boundary-layer physics.

### Standardized Timestamp Implementation:
- `timestamp_ist`: Stored as local observation timestamp (`Asia/Kolkata`, UTC+05:30).
- `timestamp_utc`: Converted directly (`timestamp_ist - 5h 30m`) for universal platform interoperability.

---

## 3. Station Identifier Harmonization & Surrogate Keys

In the upstream Parquet file, all 39 stations in Delhi shared `Station ID = site_115`, all 4 Faridabad stations shared `site_5341`, etc.

### Surrogate Key Strategy:
- Preserved the raw ID in `raw_station_id`.
- Created deterministic, collision-free surrogate keys: `f"{slugify(city)}_{slugify(station_name)}"`.
- Verified that all 56 stations in Delhi-NCR have strictly unique surrogate keys.

### Station Distribution by City & Agency:
| city      | agency   |   station_count |   avg_uptime_pct |   median_aqi |
|:----------|:---------|----------------:|-----------------:|-------------:|
| Delhi     | CPCB     |               6 |          95.0517 |      183.333 |
| Delhi     | DPCC     |              24 |          91.5838 |      183.75  |
| Delhi     | IITM     |               2 |          84.48   |      172.5   |
| Delhi     | IMD      |               7 |          86.6771 |      161     |
| Faridabad | HSPCB    |               4 |          89.9625 |      167.25  |
| Ghaziabad | UPPCB    |               3 |          95.4567 |      186.667 |
| Gurugram  | HSPCB    |               3 |          94.6133 |      171     |
| Gurugram  | IMD      |               1 |          73.99   |      141     |
| Noida     | IMD      |               1 |          91.53   |      174     |
| Noida     | UPPCB    |               5 |          95.622  |      171.4   |

---

## 4. Anomalies, Sensor Capping, and Missing Data Audit

### 4.1 Sensor Ceiling Saturation (AQI = 500)
- **Observations at Upper Limit**: **53,656** (2.2% of valid hourly observations).
- **Handling**: Preserved in full. Flagged with `is_sensor_capped = True`. Not deleted or modified, as they represent genuine severe smog episodes where particulate sensors saturated at the CPCB mathematical ceiling.

### 4.2 Out-of-Range Telemetry Anomalies (AQI > 500)
- **Total Count**: **10 occurrences** across 2.44 million readings (0.0004%).
- **Handling**: Preserved in `aqi_raw`; flagged with `is_anomalous = True`; set to `NaN` in `aqi_cleaned` so as not to distort statistical modeling.
- **Audit Log of All 10 Anomalous Readings**:

| Date | City | Station Name | Hour | Raw Recorded AQI | Issue Description |
| :--- | :--- | :--- | :--- | :---: | :--- |
| 2017-09-28 | Delhi | NSIT Dwarka Delhi CPCB | 14 | **543.0** | Value exceeds CPCB formula max (500) |
| 2017-09-28 | Delhi | NSIT Dwarka Delhi CPCB | 15 | **1182.0** | Value exceeds CPCB formula max (500) |
| 2017-10-01 | Delhi | Sirifort Delhi CPCB | 5 | **678.0** | Value exceeds CPCB formula max (500) |
| 2017-10-10 | Noida | Sector 125 Noida UPPCB | 11 | **3303.0** | Value exceeds CPCB formula max (500) |
| 2017-10-11 | Noida | Sector 125 Noida UPPCB | 11 | **2956.0** | Value exceeds CPCB formula max (500) |
| 2017-10-12 | Noida | Sector 125 Noida UPPCB | 11 | **2845.0** | Value exceeds CPCB formula max (500) |
| 2017-10-14 | Noida | Sector 125 Noida UPPCB | 11 | **2902.0** | Value exceeds CPCB formula max (500) |
| 2017-10-16 | Noida | Sector 125 Noida UPPCB | 11 | **1051.0** | Value exceeds CPCB formula max (500) |
| 2017-10-17 | Noida | Sector 125 Noida UPPCB | 11 | **3797.0** | Value exceeds CPCB formula max (500) |
| 2017-10-18 | Noida | Sector 125 Noida UPPCB | 11 | **3354.0** | Value exceeds CPCB formula max (500) |

### 4.3 Missing Data & Completeness
- **Total Missing Hours**: 222,534 (8.35%).
- **Daily Completeness Rule**: Days with $\ge 16$ valid hourly readings (100,794 out of 111,014 station-days, 90.79%) are marked `is_day_valid = True`.

---

## 5. Output Schemas & Processed File Manifest

1. **`data/processed/fact_hourly_aqi.parquet`**:
   - Rows: 2,664,336
   - Columns: 26 (station_key, timestamp_ist, timestamp_utc, aqi_raw, aqi_cleaned, aqi_category, flags)
2. **`data/processed/fact_daily_aqi.parquet` & `.csv`**:
   - Rows: 111,014
   - Columns: 23 (mean, median, min, max, completeness counts, season, diwali window)
3. **`data/processed/dim_station.parquet` & `.csv`**:
   - Rows: 56
   - Columns: 15 (station_key, raw_station_id, station_name, city, agency, uptime, coverage)
