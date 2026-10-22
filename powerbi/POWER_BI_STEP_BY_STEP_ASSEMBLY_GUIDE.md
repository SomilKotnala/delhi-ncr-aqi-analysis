# Power BI Desktop Step-by-Step Report Assembly Guide

**Project:** Delhi-NCR Air Quality Analysis (2017–2023)  
**Milestone:** Stage 3 — Business Intelligence & Power BI Desktop Report Build  
**Audience:** Data Analyst Candidate, Technical Hiring Managers, Portfolio Reviewers  
**Data Grain:** Daily Station-Level AQI (111,014 rows) & Matched Event Pairs (306 rows)  
**Target Output File:** `D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis.pbix`  

---

## 1. Executive Summary & Architecture

Power BI Desktop provides the self-service business intelligence presentation layer for this project.

Because Power BI Desktop operates via a client GUI without a headless command-line compiler for binary `.pbix` generation, all underlying data models, dimensions, DAX measures, and benchmark reconciliation matrix tables have been pre-compiled and programmatically verified in:
- **Processed Tables:** `D:\delhi-ncr-aqi-analysis\data\processed\`
- **Pre-Compiled DAX Script:** `D:\delhi-ncr-aqi-analysis\powerbi\measures.dax`
- **Benchmark Reconciliation Matrix:** `D:\delhi-ncr-aqi-analysis\powerbi\benchmarks_reconciliation.csv`
- **Automated Validation Tests:** `tests/test_powerbi_data.py` (3 passed in 1.55s)

---

## 2. Source Files & Data Schema Preparation (The 6 Required CSV Files)

All datasets are pre-exported and verified in `D:\delhi-ncr-aqi-analysis\data\processed\`. Every file serves an explicit role in the star-schema data model:

| # | File Name | Power BI Table Name | Table Grain | Primary Key | Foreign Keys / Relationships | Row Count | Visual Mapping & Purpose |
| :-: | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | **`fact_daily_aqi.csv`** | `fact_daily_aqi` | Station-Day ($s, d$) | Composite `(station_key, date)` | `station_key` $\to$ `dim_station`<br>`date` $\to$ `dim_date` | 111,014 | Core daily facts, CPCB category classifications, monthly trends, seasonal elevation |
| **2** | **`dim_station.csv`** | `dim_station` | Station ($s$) | `station_key` | 1-to-many parent to `fact_daily_aqi` and `fact_diwali_pairs` | 56 | Station metadata, physical names, cities, agencies, spatial inequality tables |
| **3** | **`dim_date.csv`** | `dim_date` | Calendar Day ($d$) | `calendar_date` | 1-to-many parent to `fact_daily_aqi` | 2,556 | 2017–2023 calendar attributes, seasons, year slicer, Diwali relative days |
| **4** | **`agg_hourly_diurnal.csv`** | `agg_hourly_diurnal` | City-Hour-Season ($c, h, w$) | Composite `(city, hour, is_winter)` | Standalone analysis table | 288 | Page 1 diurnal line chart (rush-hour vs nocturnal thermal inversion) |
| **5** | **`fact_diwali_pairs.csv`** | `fact_diwali_pairs` | Station-Year Pair ($s, y$) | Composite `(station_key, year)` | `station_key` $\to$ `dim_station`<br>`timing_cohort` $\to$ `dim_diwali_cohorts` | 306 | Page 3 matched paired differences ($t+1$ vs $t-1$), station-year surge metrics |
| **6** | **`dim_diwali_cohorts.csv`** | `dim_diwali_cohorts` | Timing Cohort ($c$) | `timing_cohort` | 1-to-many parent to `fact_diwali_pairs` | 2 | Page 3 October Diwali vs November Diwali pooled & unweighted comparison matrix |

---

## 3. Step-by-Step Power BI Desktop Build Instructions

### Step 3.1: Launch Power BI Desktop & Load All 6 CSV Tables
1. Launch **Power BI Desktop** from Windows Start Menu or run:
   ```powershell
   Start-Process PBIDesktop
   ```
2. In the splash dialog, click **Get Data** > select **Text/CSV** > click **Connect**.
3. Navigate to `D:\delhi-ncr-aqi-analysis\data\processed\`:
   - Select `fact_daily_aqi.csv` $\to$ click **Transform Data** (opens Power Query Editor).
   - In Power Query, verify `date` is set to **Date**, `daily_mean_aqi` is set to **Decimal Number**, and `is_day_valid` is set to **True/False**.
   - On the Home ribbon, click **New Source** > **Text/CSV** > load `dim_station.csv`.
   - On the Home ribbon, click **New Source** > **Text/CSV** > load `dim_date.csv` (verify `calendar_date` is **Date**).
   - On the Home ribbon, click **New Source** > **Text/CSV** > load `agg_hourly_diurnal.csv`.
   - On the Home ribbon, click **New Source** > **Text/CSV** > load `fact_diwali_pairs.csv` (verify `paired_surge` is **Decimal Number**, `is_elevated` is **True/False**).
   - On the Home ribbon, click **New Source** > **Text/CSV** > load `dim_diwali_cohorts.csv`.
4. Click **Close & Apply** on the top-left ribbon.

---

### Step 3.2: Configure Model Relationships (Star Schema)
Navigate to **Model View** (left navigation bar, third icon):
1. **`dim_station` to `fact_daily_aqi`**:
   - Drag `dim_station[station_key]` to `fact_daily_aqi[station_key]`.
   - Cardinality: **One to Many (1:*)**, Cross filter: **Single**, Active: **Checked**.
2. **`dim_date` to `fact_daily_aqi`**:
   - Drag `dim_date[calendar_date]` to `fact_daily_aqi[date]`.
   - Cardinality: **One to Many (1:*)**, Cross filter: **Single**, Active: **Checked**.
3. **`dim_station` to `fact_diwali_pairs`**:
   - Drag `dim_station[station_key]` to `fact_diwali_pairs[station_key]`.
   - Cardinality: **One to Many (1:*)**, Cross filter: **Single**, Active: **Checked**.
4. **`dim_diwali_cohorts` to `fact_diwali_pairs`**:
   - Drag `dim_diwali_cohorts[timing_cohort]` to `fact_diwali_pairs[timing_cohort]`.
   - Cardinality: **One to Many (1:*)**, Cross filter: **Single**, Active: **Checked**.

---

### Step 3.3: Create the DAX Measure Table
1. On the Home ribbon, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Right-click `_Measures` in the Data pane > click **New Measure**.
4. Open `D:\delhi-ncr-aqi-analysis\powerbi\measures.dax` and copy each measure:
   - `[Median AQI]`
   - `[Mean AQI]`
   - `[AQI IQR]`
   - `[Valid Station-Days]`
   - `[Total Scheduled Station-Days]`
   - `[Data Completeness %]`
   - `[Severe AQI Days Count]`
   - `[Severe AQI Days %]`
   - `[Sensor Capped Days Count]`
   - `[Sensor Capped Days %]`
   - `[Winter Median AQI]`
   - `[Non-Winter Median AQI]`
   - `[Winter Elevation Absolute]`
   - `[Winter Elevation Ratio]`
   - `[Diwali Matched Station-Years]`
   - `[Diwali Pooled Mean Surge]`
   - `[Diwali Pooled Median Surge]`
   - `[Diwali Station-Years Elevated %]`
   - `[October Diwali Pooled Mean Surge]`
   - `[November Diwali Pooled Mean Surge]`
5. Delete the default blank `Column1` from `_Measures` to make it a pure measure folder.

---

## 4. Visual Assembly Across Three Report Pages

### Page 1: Regional AQI Overview & Health Risk
Rename page to: **Regional AQI Overview**
1. **Global Header Slicers (Top Ribbon):**
   - **City Slicer:** Tile slicer with `dim_station[city]` (`Delhi`, `Faridabad`, `Ghaziabad`, `Gurugram`, `Noida`).
   - **Year Slicer:** Dropdown slicer with `dim_date[year]` (`2017` to `2023`).
   - **Station Slicer:** Dropdown slicer with `dim_station[station_name]`.
2. **Headline KPI Cards (Row 1):**
   - **Card 1:** Field: `[Median AQI]`. Format: 1 decimal place. Expected: **`199.3`**.
   - **Card 2:** Field: `[Data Completeness %]`. Format: 1 decimal place. Expected: **`90.8%`** (Denominator: 111,014).
   - **Card 3:** Field: `[Severe AQI Days %]`. Accent color: Crimson `#E60000`. Expected: **`6.3%`**.
   - **Card 4:** Field: `[Sensor Capped Days %]`. Accent color: Maroon `#7A0019`. Expected: **`12.4%`**.
3. **Monthly Trajectory (Row 2, Left):**
   - Visual: **Line Chart**.
   - X-Axis: `dim_date[calendar_date]` (formatted as Year-Month).
   - Y-Axis: `[Median AQI]`, `[Mean AQI]`.
4. **CPCB Category Distribution (Row 2, Right):**
   - Visual: **Donut Chart**.
   - Legend: `fact_daily_aqi[daily_category]`.
   - Values: `[Valid Station-Days]`.
   - Map slice colors to statutory CPCB hex codes (see Section 5).
5. **City Rankings & Diurnal Profiles (Row 3):**
   - **Left:** Clustered Bar Chart: X-Axis: `dim_station[city]`, Y-Axis: `[Median AQI]`.
   - **Right:** Line Chart from `agg_hourly_diurnal`: X-Axis: `hour`, Y-Axis: `median_aqi`, Legend: `is_winter`.

---

### Page 2: Seasonal Inversion & Spatial Dynamics
Rename page to: **Seasonal & Spatial Dynamics**
1. **Seasonal Comparison Cards (Row 1):**
   - **Card 1:** `[Winter Median AQI]`. Expected: **`335.6`**.
   - **Card 2:** `[Non-Winter Median AQI]`. Expected: **`154.0`**.
   - **Card 3:** `[Winter Elevation Absolute]`. Expected: **`+181.6 pts`**.
   - **Card 4:** `[Winter Elevation Ratio]`. Expected: **`2.18x`**.
2. **City Winter vs Non-Winter Distribution (Row 2, Left):**
   - Visual: **Clustered Column Chart**.
   - X-Axis: `dim_station[city]`.
   - Legend: `dim_date[is_winter]`.
   - Values: `[Median AQI]`.
3. **Meteorological Seasonality (Row 2, Right):**
   - Visual: **Clustered Column Chart**.
   - X-Axis: `dim_date[season]` (`Winter`, `Pre-Monsoon`, `Monsoon`, `Post-Monsoon`).
   - Values: `[Median AQI]`.
4. **Spatial Inequality Tables (Row 3):**
   - **Table 1 (Top 10 Most Polluted):** Fields: `station_name`, `city`, `[Median AQI]`, `[Severe AQI Days %]`. Sorted descending by `[Median AQI]`.
   - **Table 2 (Top 10 Cleanest):** Fields: `station_name`, `city`, `[Median AQI]`, `[Severe AQI Days %]`. Sorted ascending by `[Median AQI]`.
5. **Statistical Robustness Callout Box:**
   - Multi-row text box detailing:
     - 14-day Moving Block Bootstrap 95% CI: **$[156.98, 202.14]$ AQI points**.
     - Right-Censored Tobit Latent Shift: **$+154.17$ latent AQI points** ($p < 10^{-15}$).

---

### Page 3: Diwali Episode Analysis & Confounding Audit
Rename page to: **Diwali Episode Analysis**
1. **Episode KPI Cards (Row 1):**
   - **Card 1:** `[Diwali Pooled Mean Surge]`. Expected: **`+81.57`**.
   - **Card 2:** `[Diwali Pooled Median Surge]`. Expected: **`+80.38`**.
   - **Card 3:** `[Diwali Station-Years Elevated %]`. Expected: **`85.95%`**.
   - **Card 4:** `[Diwali Matched Station-Years]`. Expected: **`306 pairs`**.
2. **Event Study Window Trajectory (Row 2):**
   - Visual: **Line Chart** from `fact_daily_aqi`.
   - Filter page or visual: `diwali_relative_day` is between `-7` and `+7`.
   - X-Axis: `dim_date[diwali_relative_day]`.
   - Y-Axis: `[Median AQI]`.
   - Legend: `dim_date[year]`.
   - Add reference dashed line at `X = 0` (Diwali Festival Night).
3. **Timing Cohort Comparison (Row 3):**
   - **Left:** Clustered Bar Chart from `fact_diwali_pairs`:
     - X-Axis: `year`.
     - Y-Axis: `Average of paired_surge`.
     - Legend / Color: `timing_cohort` (`October Diwali` vs `November Diwali`).
   - **Right:** Matrix Table from `dim_diwali_cohorts`:
     - Rows: `timing_cohort`.
     - Values: `years_count`, `matched_station_years`, `pooled_mean_surge`, `pooled_pct_elevated`, `unweighted_annual_pct_elevated`.
4. **Causal Deconfounding Disclaimer Callout:**
   - Callout box articulating:
     1. Regional Agricultural Burning overlap (Oct 25 – Nov 15).
     2. Planetary Boundary Layer Height (PBLH) Collapse ($>1500\text{m} \to <300\text{m}$).
     3. Statutory Sensor Ceiling Compression ($500.0$ ceiling dampens observable surge on high baselines).

---

## 5. Official Statutory CPCB Color Palette

In Power BI, navigate to **View** > **Themes** > **Customize Current Theme** and set the statutory palette:

| Category | AQI Range | Hex Code | Visual Meaning |
| :--- | :---: | :---: | :--- |
| **Good** | $0 - 50$ | `#00B050` | Minimal health impact |
| **Satisfactory** | $51 - 100$ | `#92D050` | Minor breathing discomfort to sensitive people |
| **Moderate** | $101 - 200$ | `#E6B800` | Breathing discomfort to people with lung/heart disease |
| **Poor** | $201 - 300$ | `#FF8C00` | Breathing discomfort to most people on prolonged exposure |
| **Very Poor** | $301 - 400$ | `#E60000` | Respiratory illness on prolonged exposure |
| **Severe** | $401 - 500+$ | `#7A0019` | Affects healthy people; serious impacts on respiratory disease |

---

## 6. Verification, Validation Protocol & Sign-Off Checklist

### 6.1 Four-Tier Verification Protocol
To ensure 100% analytical honesty, this project strictly separates data verification into four distinct architectural tiers:

1. **Tier 1: PostgreSQL SQL Ground Truth (`VERIFIED_DB`)**  
   Executed directly in PostgreSQL 18 (`localhost:5432 / delhi_aqi`) via `sql/analytical_queries.sql`.
2. **Tier 2: Python / Streamlit Analytical Engine (`VERIFIED_PARQUET`)**  
   Executed directly in Python 3.14 via `dashboard/metrics.py` and validated by 59 automated pytest tests.
3. **Tier 3: DAX Formulas Prepared for Power BI**  
   Pre-compiled in `powerbi/measures.dax` and documented in `docs/POWER_BI_DASHBOARD_GUIDE.md`.
4. **Tier 4: Power BI Desktop Runtime Results (`Expected / Pending Power BI Validation`)**  
   Benchmarks listed in `powerbi/benchmarks_reconciliation.csv` represent the *expected targets* for Power BI. They are marked **"Expected / Pending Power BI Validation"** until the `.pbix` report is manually assembled in Power BI Desktop and callout values are visually verified on the canvas.

### 6.2 Visual Inspection Checklist in Power BI Desktop
After assembling the visuals, cross-examine each visual callout value against `powerbi/benchmarks_reconciliation.csv`:

- [ ] **Page 1:** Network Median AQI displays **`199.3`** (Mean: `213.6`)
- [ ] **Page 1:** Valid Station-Days displays **`100,794`**
- [ ] **Page 1:** Data Completeness displays **`90.8%`** (Denominator: 111,014 scheduled days)
- [ ] **Page 1:** Severe Days % displays **`6.3%`** (6,389 days)
- [ ] **Page 1:** Sensor Capped Days % displays **`12.4%`** (12,536 days)
- [ ] **Page 2:** Winter Median displays **`335.6`** vs Non-Winter **`154.0`** (Elevation: **`+181.6 pts`**, **`2.18x`**)
- [ ] **Page 3:** Diwali Matched Station-Years displays **`306 pairs`**
- [ ] **Page 3:** Diwali Pooled Mean Surge displays **`+81.57`** (Pooled Median: **`+80.38`**)
- [ ] **Page 3:** Diwali Station-Years Elevated displays **`85.95%`** (263 / 306 pairs)
- [ ] **Page 3:** October Diwali displays **`+58.9 pts`** pooled surge (84.3% pooled up, 86.3% unweighted avg)
- [ ] **Page 3:** November Diwali displays **`+93.9 pts`** pooled surge (86.9% pooled up, 87.2% unweighted avg)

### 6.3 Saving the Authoritative Report
Once the visual checklist passes, click **File** > **Save As** and save directly to:  
`D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis.pbix`  
*Do not claim runtime completion until the `.pbix` file exists on disk and is confirmed.*
