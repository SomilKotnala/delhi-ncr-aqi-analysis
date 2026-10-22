# Power BI Desktop Dashboard Guide: Delhi-NCR Air Quality

**Project:** Delhi-NCR Air Quality Analysis (2017–2023)  
**Milestone:** Stage 3 — Business Intelligence & Reporting Architecture  
**Target Audience:** Beginner Data Analyst Candidates, Hiring Managers & Interview Reviewers  
**Data Grain:** Daily Station-Level AQI (111,014 records across 56 stations)  

---

## 1. Prerequisites & Source Datasets

Power BI Desktop is installed on the local system (`C:\Users\Dell\AppData\Local\Microsoft\WindowsApps\PBIDesktopStore.exe`).

The dimensional data model is prepared and exported in `D:\delhi-ncr-aqi-analysis\data\processed\`:

1. **`fact_daily_aqi.csv` / `fact_daily_aqi.parquet`** (111,014 rows):
   - Daily measurements: `station_key`, `date` (`calendar_date`), `daily_mean_aqi`, `daily_median_aqi`, `daily_min_aqi`, `daily_max_aqi`, `total_hours`, `valid_hours_count`, `capped_hours_count`, `is_day_valid`, `daily_category`, `is_winter`, `is_diwali_window`, `diwali_relative_day`.
2. **`dim_station.csv` / `dim_station.parquet`** (56 rows):
   - Station metadata: `station_key`, `raw_station_id`, `station_name`, `city`, `state`, `agency`, `total_recorded_days`, `uptime_hourly_pct`, `temporal_coverage_pct`.
3. **`dim_date.csv` / `dim_date.parquet`** (2,556 rows, 2017–2023):
   - Calendar attributes: `calendar_date`, `year`, `month`, `month_name`, `day`, `day_of_week`, `day_name`, `is_weekend`, `season`, `is_winter`, `is_diwali_window`, `diwali_relative_day`.
4. **`agg_hourly_diurnal.csv`** (288 rows):
   - Pre-aggregated 24-hour diurnal statistics: `city`, `hour`, `is_winter`, `count`, `mean_aqi`, `median_aqi`, `p25_aqi`, `p75_aqi`, `capped_count`.

---

## 2. Step-by-Step Power BI Model Setup

### Step 2.1: Import Data into Power BI Desktop
1. Open **Power BI Desktop**.
2. On the **Home** ribbon, select **Get Data** > **Text/CSV** (or **Folder**).
3. Browse to `D:\delhi-ncr-aqi-analysis\data\processed\`:
   - Select `fact_daily_aqi.csv` $\to$ click **Transform Data** (Power Query Editor).
   - In Power Query, confirm `date` is set to **Date** type and `daily_mean_aqi` is set to **Decimal Number**.
   - Select **New Source** > **Text/CSV** > load `dim_station.csv`.
   - Select **New Source** > **Text/CSV** > load `dim_date.csv` (set `calendar_date` to **Date** type).
   - Select **New Source** > **Text/CSV** > load `agg_hourly_diurnal.csv`.
4. Click **Close & Apply** on the Home ribbon.

### Step 2.2: Establish Star Schema Relationships
Navigate to the **Model View** (left navigation bar, bottom icon):
1. Locate `fact_daily_aqi` at the center.
2. Drag `dim_station[station_key]` to `fact_daily_aqi[station_key]`:
   - Cardinality: **One to Many (1:*)**
   - Cross filter direction: **Single**
   - Active: **Checked**
3. Drag `dim_date[calendar_date]` to `fact_daily_aqi[date]`:
   - Cardinality: **One to Many (1:*)**
   - Cross filter direction: **Single**
   - Active: **Checked**

```
 ┌──────────────────────┐                     ┌──────────────────────┐
 │     dim_station      │                     │       dim_date       │
 ├──────────────────────┤                     ├──────────────────────┤
 │ PK station_key       │(1)               (1)│ PK calendar_date     │
 │    station_name      │  │               │  │    year              │
 │    city              │  │               │  │    month_name        │
 │    agency            │  │               │  │    season            │
 │    temporal_cov_pct  │  │               │  │    is_winter         │
 └──────────────────────┘  │               │  └──────────────────────┘
                           │   ┌───────┐   │
                           └──>│  (*)  │<──┘
                               │ Fact  │
                               └───────┘
                                   │
                     ┌───────────────────────────┐
                     │      fact_daily_aqi       │
                     ├───────────────────────────┤
                     │ FK station_key            │
                     │ FK date (calendar_date)   │
                     │    daily_mean_aqi         │
                     │    daily_median_aqi       │
                     │    valid_hours_count      │
                     │    capped_hours_count     │
                     │    is_day_valid           │
                     │    daily_category         │
                     └───────────────────────────┘
```

---

## 3. Audited DAX Measures Specification

Create a dedicated measure table: on the **Home** ribbon, select **Enter Data**, name the table `_DAX_Measures`, and enter the following copy-paste ready formulas:

### Measure 1: Network Median Daily AQI
```dax
Median AQI = 
CALCULATE(
    MEDIAN('fact_daily_aqi'[daily_mean_aqi]),
    'fact_daily_aqi'[is_day_valid] = TRUE()
)
```
*Benchmark Verification:* Full network baseline = `199.29`.

### Measure 2: Network Mean Daily AQI
```dax
Mean AQI = 
CALCULATE(
    AVERAGE('fact_daily_aqi'[daily_mean_aqi]),
    'fact_daily_aqi'[is_day_valid] = TRUE()
)
```
*Benchmark Verification:* Full network baseline = `213.56`.

### Measure 3: Valid Monitored Station-Days
```dax
Valid Station-Days = 
CALCULATE(
    COUNTROWS('fact_daily_aqi'),
    'fact_daily_aqi'[is_day_valid] = TRUE()
)
```
*Benchmark Verification:* Full network baseline = `100,794`.

### Measure 4: Data Completeness Rate (%)
```dax
Data Completeness % = 
VAR TotalDays = COUNTROWS('fact_daily_aqi')
VAR ValidDays = [Valid Station-Days]
RETURN
DIVIDE(ValidDays, TotalDays, 0) * 100
```
*Benchmark Verification:* Full network baseline = `90.79%`.

### Measure 5: Severe AQI Days Share (%)
```dax
Severe Days % = 
VAR SevereCount = 
    CALCULATE(
        COUNTROWS('fact_daily_aqi'),
        'fact_daily_aqi'[is_day_valid] = TRUE(),
        'fact_daily_aqi'[daily_mean_aqi] > 400
    )
VAR ValidDays = [Valid Station-Days]
RETURN
DIVIDE(SevereCount, ValidDays, 0) * 100
```
*Benchmark Verification:* Full network baseline = `6.34%` (6,389 station-days).

### Measure 6: Sensor Ceiling Saturation Share (%)
```dax
Sensor Capped Days % = 
VAR CappedCount = 
    CALCULATE(
        COUNTROWS('fact_daily_aqi'),
        'fact_daily_aqi'[is_day_valid] = TRUE(),
        'fact_daily_aqi'[capped_hours_count] > 0
    )
VAR ValidDays = [Valid Station-Days]
RETURN
DIVIDE(CappedCount, ValidDays, 0) * 100
```
*Benchmark Verification:* Full network baseline = `12.44%` (12,536 station-days).

### Measure 7: Winter Median AQI
```dax
Winter Median AQI = 
CALCULATE(
    [Median AQI],
    'dim_date'[is_winter] = TRUE()
)
```
*Benchmark Verification:* Full network baseline = `335.61`.

### Measure 8: Non-Winter Median AQI
```dax
Non-Winter Median AQI = 
CALCULATE(
    [Median AQI],
    'dim_date'[is_winter] = FALSE()
)
```
*Benchmark Verification:* Full network baseline = `154.00`.

### Measure 9: Winter Excess Elevation (Absolute & Ratio)
```dax
Winter Elevation Absolute = 
[Winter Median AQI] - [Non-Winter Median AQI]

Winter Elevation Ratio = 
DIVIDE([Winter Median AQI], [Non-Winter Median AQI], 0)
```
*Benchmark Verification:* Absolute = `+181.61 pts`, Ratio = `2.18x`.

### Measure 10: Station-Matched Post-Diwali Surge
```dax
Diwali Matched Surge = 
VAR PreDiwaliAQI = 
    CALCULATE(
        [Median AQI],
        'dim_date'[diwali_relative_day] = -1
    )
VAR PostDiwaliAQI = 
    CALCULATE(
        [Median AQI],
        'dim_date'[diwali_relative_day] = 1
    )
RETURN
PostDiwaliAQI - PreDiwaliAQI
```
*Benchmark Verification:* 7-year multi-year paired median surge = `+72.48 pts`.

---

## 4. Multi-Page Report Layout & Visual Configuration

### Page 1: Regional AQI Overview & Health Risk
- **Page Size:** 16:9 widescreen (1280 × 720 px).
- **Global Slicers (Top Bar):**
  - City: Tile / Horizontal Buttons (`Delhi`, `Faridabad`, `Ghaziabad`, `Gurugram`, `Noida`).
  - Year: Dropdown (`2017` to `2023`).
  - Station Name: Searchable single-select dropdown.
- **Row 1: KPI Cards (4 Cards across top):**
  1. Card: `[Median AQI]` | Callout value: `199.3` | Subtitle: "Mean: 213.6 | Valid Obs: 100.8k".
  2. Card: `[Valid Station-Days]` | Callout value: `100,794` | Subtitle: "Completeness: 90.8%".
  3. Card: `[Severe Days %]` | Callout value: `6.3%` | Accent color: Crimson `#E60000`.
  4. Card: `[Sensor Capped Days %]` | Callout value: `12.4%` | Accent color: Maroon `#7A0019`.
- **Row 2: Primary Visuals:**
  - **Left (Line Chart, width 65%):**
    - X-Axis: `dim_date[year_month]`.
    - Y-Axis: `[Median AQI]`, `[Mean AQI]`.
    - Reference Bands: Add Constant Lines / Error Bars for CPCB categories.
  - **Right (Donut Chart, width 35%):**
    - Legend: `fact_daily_aqi[daily_category]`.
    - Values: `[Valid Station-Days]`.
    - Color Data: Custom color per category (see palette below).
- **Row 3: City Rankings & Diurnal Dynamics:**
  - **Left (Clustered Bar Chart):** X-Axis: `dim_station[city]`, Y-Axis: `[Median AQI]`.
  - **Right (Line Chart from `agg_hourly_diurnal`):** X-Axis: `hour`, Y-Axis: `median_aqi`, Legend: `is_winter`.

---

### Page 2: Seasonal Inversion & Spatial Dynamics
- **Row 1: Seasonal Comparison Cards:**
  - Card 1: `[Winter Median AQI]` (`335.61`).
  - Card 2: `[Non-Winter Median AQI]` (`154.00`).
  - Card 3: `[Winter Elevation Absolute]` (`+181.61 pts`).
  - Card 4: `[Winter Elevation Ratio]` (`2.18x`).
- **Row 2: Distribution Visuals:**
  - **Clustered Column Chart:** X-Axis: `dim_station[city]`, Legend: `dim_date[is_winter]`, Values: `[Median AQI]`.
  - **Box & Whisker / Clustered Column Chart:** X-Axis: `dim_date[season]`, Values: `[Median AQI]`.
- **Row 3: Spatial Inequality Ranking (Top 10 vs Bottom 10):**
  - **Table 1 (Most Polluted):** `station_name`, `city`, `[Median AQI]`, `[Severe Days %]`. Top 10 by `[Median AQI]`.
  - **Table 2 (Cleanest):** `station_name`, `city`, `[Median AQI]`, `[Severe Days %]`. Bottom 10 by `[Median AQI]`.
- **Row 4: Statistical Methodology Callout Card:**
  - Text box highlighting the Moving Block Bootstrap ($L=14$ days, 95% CI $[156.98, 202.14]$) and the Tobit sensor-censored estimate (+154.17 pts).

---

### Page 3: Diwali Episode Analysis & Confounding Audit
- **Row 1: Episode Summary Cards:**
  - Card 1: Multi-Year Mean Surge (`+65.7 pts`).
  - Card 2: Multi-Year Median Surge (`+72.5 pts`).
  - Card 3: Stations Elevated % (`84.8%`).
  - Card 4: Matched Station Pairs (`281 pairs`).
- **Row 2: Event Timeline ($t-7$ to $t+7$):**
  - **Line Chart:** X-Axis: `dim_date[diwali_relative_day]`, Y-Axis: `[Median AQI]`, Legend: `dim_date[year]`.
  - Vertical Reference Line at `X = 0` (Diwali Day).
- **Row 3: Timing Cohort Comparison (Late October vs Mid November):**
  - **Clustered Bar Chart:** X-Axis: `year`, Y-Axis: `[Diwali Matched Surge]`.
  - **Matrix Table:** Cohort (`Late Oct` vs `Mid Nov`), Pre-Diwali Baseline Median, Post-Diwali Peak Median, Mean Surge.
- **Row 4: Causal Confounding Callout:**
  - Analytical note explaining the co-occurrence of agricultural burning and boundary layer collapse.

---

## 5. Official CPCB Palette Hex Codes

In Power BI, navigate to **View** > **Themes** > **Customize Current Theme** and map the statutory CPCB colors:

| Category | AQI Range | Hex Code | Visual Purpose |
| :--- | :---: | :---: | :--- |
| **Good** | $0 - 50$ | `#00B050` | Healthy baseline |
| **Satisfactory** | $51 - 100$ | `#92D050` | Acceptable quality |
| **Moderate** | $101 - 200$ | `#E6B800` | High-visibility yellow on white background |
| **Poor** | $201 - 300$ | `#FF8C00` | Warning orange |
| **Very Poor** | $301 - 400$ | `#E60000` | High risk crimson |
| **Severe** | $401 - 500+$ | `#7A0019` | Emergency dark maroon |

---

## 6. Pre-Publish Verification Checklist

- [x] All 3 tables imported without type conversion errors (`date` is Date, `aqi` is Decimal).
- [x] Star schema relationships are 1:Many with Single cross-filter direction (no bidirectional filters).
- [x] All 10 DAX measures verified against `reports/DASHBOARD_VALIDATION_REPORT.md` (all 10 match benchmark values).
- [x] Slicers dynamically filter all visual cards without breaking card formulas.
- [x] Tooltips enabled on all charts with informative formatted values (`%.1f`).
- [x] Statutory 500.0 sensor ceiling explicitly documented on visual cards and callouts.
- [x] File saved locally as `delhi_ncr_aqi_dashboard.pbix`.
