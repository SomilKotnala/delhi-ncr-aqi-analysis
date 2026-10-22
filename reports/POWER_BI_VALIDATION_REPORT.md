# Power BI Desktop Report Validation & Runtime Reconciliation Report

**Project Name:** Delhi-NCR Air Quality Analysis: Seasonal Trends, Spatial Differences, and Diwali Pollution Episodes  
**Project Root:** `D:\delhi-ncr-aqi-analysis`  
**Report File:** `D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis.pbix`  
**Backup Original File:** `D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_original.pbix`  
**Evaluation Date:** October 22, 2026  
**Auditor:** Antigravity Autonomous Coding & Analytics Engine  
**Validation Outcome:** **100% RUNTIME VERIFIED (21/21 DAX Measures Executed in Power BI Desktop Tabular Engine)**

---

## 1. Executive Summary

This audit report validates the Power BI Desktop data model, dimensional relationships, and DAX calculations for the Delhi-NCR Air Quality Analysis project. 

Rather than relying on theoretical formula checks or estimated values, this audit established an active **ADOMD.NET binary connection directly to the live Microsoft SQL Server Analysis Services Tabular instance (`msmdsrv.exe`) spawned by Power BI Desktop**. Every single DAX measure in the `_Measures` table was evaluated against the in-memory VertiPaq tabular model across the 7-year monitoring window (2017–2023).

### Key Audit Findings:
1. **100% Benchmark Alignment:** All 21 core DAX measures executed with zero syntax or calculation errors and matched the verified PostgreSQL 18 database ground-truth and Python analytical outputs to the decimal place.
2. **True Completeness Preserved:** The DAX measure `[Data Completeness %]` correctly computes `DIVIDE([Valid Station-Days], [Total Scheduled Station-Days], 0)`, evaluating to **90.79%** ($100,794 / 111,014$). It avoids the common BI pitfall of pre-filtering invalid records which would artificially collapse completeness to 100%.
3. **Regional vs. Municipal Scope Precision:** Network Median AQI (**199.29**) and Mean AQI (**213.56**) correctly reflect the 5-city pooled regional network ($N = 100,794$). When filtered to Delhi City alone, the DAX measures dynamically evaluate to Mean = **215.44** and IQR = **187.40**, resolving earlier municipal subset discrepancies.
4. **Diwali Pair Denominator Integrity:** Matched station-year pairs correctly evaluate to **306** across the 7 festival years (2017–2023), confirming that the denominator represents station-year pairs rather than unique monitoring stations ($N = 56$). Pooled mean surge (+81.57 AQI points) and station-years elevated (85.95%) match pre-registered econometric models.

---

## 2. Live Runtime Verification Environment

Power BI Desktop was audited in its active execution environment:

| Property | Value / Specification |
| :--- | :--- |
| **Power BI Desktop Executable** | `C:\Users\Dell\AppData\Local\Microsoft\WindowsApps\PBIDesktopStore.exe` (Version 2.159.883.0 x64) |
| **Host Process IDs** | `PBIDesktop.exe` (PID 5748, 7044) |
| **Analysis Services Engine** | `msmdsrv.exe` (PID 25716) |
| **Local Listening Port** | `127.0.0.1:50910` (TCP Loopback) |
| **Active Tabular Catalog** | `2e9e0933-fbc0-486a-9963-ce244a48d6a0` |
| **Interface Driver** | `Microsoft.PowerBI.AdomdClient.dll` |
| **PBIX Internal Format** | PBIR (Power BI Enhanced Report Schema 2.0.0, Page 2.1.0, Container 2.14.0) |
| **Verification Method** | Automated DAX Query Batch via ADOMD.NET Data Adapter (`powerbi/query_dax_runtime.ps1`) |

---

## 3. Master 21-KPI Runtime Reconciliation Matrix

The following table presents the ground-truth benchmark comparison across the four operational tiers:
- **Tier 1 (SQL):** PostgreSQL 18 `delhi_aqi` database.
- **Tier 2 (Python):** Processed Parquet files evaluated via Pandas in the Streamlit engine.
- **Tier 3 (DAX Formula):** Pre-compiled DAX expressions in `_Measures`.
- **Tier 4 (Power BI Runtime):** Actual value returned by `msmdsrv.exe` on port 50910.

| Metric ID | Metric Name | Report Page | Target Reference | Live Power BI Runtime Result | Absolute Difference | Verification Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **M01** | Network Median AQI | Page 1 | 199.29 | **199.29** | 0.00 | **PASS (VERIFIED)** |
| **M02** | Network Mean AQI | Page 1 | 213.56 | **213.5617** | 0.00 | **PASS (VERIFIED)** |
| **M03** | AQI Interquartile Range (IQR) | Page 1 | 185.17 | **185.1700** | 0.00 | **PASS (VERIFIED)** |
| **M04** | Valid Station-Days Count | Page 1 | 100,794 | **100,794** | 0 | **PASS (VERIFIED)** |
| **M05** | Total Scheduled Station-Days | Page 1 | 111,014 | **111,014** | 0 | **PASS (VERIFIED)** |
| **M06** | Data Completeness % | Page 1 | 90.79% | **90.79%** (0.90794) | 0.00% | **PASS (VERIFIED)** |
| **M07** | Severe AQI Days Count | Page 1 | 6,389 | **6,389** | 0 | **PASS (VERIFIED)** |
| **M08** | Severe AQI Days % | Page 1 | 6.34% | **6.3387%** | 0.00% | **PASS (VERIFIED)** |
| **M09** | Sensor Capped Days Count | Page 1 | 12,536 | **12,536** | 0 | **PASS (VERIFIED)** |
| **M10** | Sensor Capped Days % | Page 1 | 12.44% | **12.4372%** | 0.00% | **PASS (VERIFIED)** |
| **M11** | Winter Median AQI | Page 2 | 335.61 | **335.61** | 0.00 | **PASS (VERIFIED)** |
| **M12** | Non-Winter Median AQI | Page 2 | 154.00 | **154.00** | 0.00 | **PASS (VERIFIED)** |
| **M13** | Winter Elevation Absolute | Page 2 | +181.61 pts | **+181.61 pts** | 0.00 | **PASS (VERIFIED)** |
| **M14** | Winter Elevation Ratio | Page 2 | 2.18x | **2.1793x** | 0.00 | **PASS (VERIFIED)** |
| **M15** | Diwali Matched Station-Years | Page 3 | 306 | **306** | 0 | **PASS (VERIFIED)** |
| **M16** | Diwali Pooled Mean Surge | Page 3 | +81.57 pts | **+81.5677 pts** | 0.00 | **PASS (VERIFIED)** |
| **M17** | Diwali Pooled Median Surge | Page 3 | +80.38 pts | **+80.3800 pts** | 0.00 | **PASS (VERIFIED)** |
| **M18** | Diwali Station-Years Elevated %| Page 3 | 85.95% | **85.9477%** | 0.00% | **PASS (VERIFIED)** |
| **M19** | October Diwali Pooled Mean Surge | Page 3 | +58.92 pts | **+58.9169 pts** | 0.00 | **PASS (VERIFIED)** |
| **M20** | November Diwali Pooled Mean Surge| Page 3 | +93.92 pts | **+93.9227 pts** | 0.00 | **PASS (VERIFIED)** |
| **M21** | Diwali Elevated Station-Years Count | Page 3 | 263 | **263** | 0 | **PASS (VERIFIED)** |

---

## 4. Deep-Dive Analytical Investigations

### 4.1 Data Completeness Denominator (90.79% vs. 100.0%)
- **The Problem:** In many naive Power BI models, developers create a calculated measure `[Data Completeness %] = DIVIDE(COUNTROWS(fact_daily_aqi), CALCULATE(COUNTROWS(fact_daily_aqi), ALL(fact_daily_aqi)))` or filter the fact table at the Power Query ingestion stage to `is_day_valid == TRUE`. If invalid rows are filtered out at ingestion, the denominator shrinks to valid days only, producing a misleading completeness rate of 100.0%.
- **Verified Implementation:** In `_Measures`:
  ```dax
  Total Scheduled Station-Days = COUNTROWS('fact_daily_aqi')
  Valid Station-Days = CALCULATE(COUNTROWS('fact_daily_aqi'), 'fact_daily_aqi'[is_day_valid] = TRUE())
  Data Completeness % = DIVIDE([Valid Station-Days], [Total Scheduled Station-Days], 0)
  ```
- **Audit Verification:** The model retains all 111,014 scheduled calendar station-days in `fact_daily_aqi`. Evaluating `[Data Completeness %]` yields **0.9079395** (**90.79%**), which exactly reflects the 10,220 invalid station-days where fewer than 16 valid hourly readings were recorded.

### 4.2 Regional Network vs. Municipal Scope
- **The Problem:** Prior audit notes observed a discrepancy where the mean AQI was reported as 215.44 and IQR as 187.40 in some reports, versus 213.56 and 185.17 in others.
- **Audit Verification:**
  - When the star schema evaluates across all 5 monitored NCR cities (Delhi, Faridabad, Ghaziabad, Gurugram, Noida), $N = 100,794$ station-days, producing Network Mean = **213.56**, Median = **199.29**, and IQR = **185.17**.
  - When sliced by `dim_station[city] = "Delhi"` ($N = 73,498$ station-days across 39 stations), the arithmetic mean rises to **215.44** and IQR expands to **187.40**.
  - The Power BI DAX measures are dynamic: with no slicer active, they represent the true 5-city regional network; when filtered by the city slicer, they dynamically adapt to municipal subsets without hardcoding.

### 4.3 Severe AQI vs. Sensor-Capped Station-Days
- **Severe AQI Days (6.34%):** Evaluated as station-days where `daily_mean_aqi > 400.0` and `is_day_valid == TRUE`. Runtime count: **6,389 days** out of 100,794 valid days (**6.34%**).
- **Sensor-Capped Days (12.44%):** Evaluated as station-days where at least one hourly reading hit the statutory reporting ceiling of 500 (`capped_hours_count > 0`). Runtime count: **12,536 days** out of 100,794 valid days (**12.44%**).
- **Audit Conclusion:** The model maintains strict separation between statutory severity (daily average > 400) and sensor ceiling truncation (hourly AQI = 500). Documentation correctly distinguishes statutory reporting caps from physical sensor saturation.

### 4.4 Diwali Matched Station-Year Pairs & Timing Cohorts
- **Unit of Observation:** The festival event analysis compares the pre-Diwali baseline ($t-1$) with the post-Diwali day ($t+1$). Valid pairing requires valid daily readings on both days. Over the 7 festival years (2017–2023), this yields exactly **306 matched station-year pairs** across 56 unique monitoring stations.
- **Pooled vs. Unweighted Cohorts:**
  - **October Diwali (2017, 2019, 2022; $N = 108$ pairs):** Pooled mean surge is **+58.92 AQI points**, pooled median surge is **+59.23 AQI points**, and **84.26%** (91/108) of pairs elevated. Unweighted annual average is 86.32%.
  - **November Diwali (2018, 2020, 2021, 2023; $N = 198$ pairs):** Pooled mean surge is **+93.92 AQI points**, pooled median surge is **+92.54 AQI points**, and **86.87%** (172/198) of pairs elevated. Unweighted annual average is 87.21%.
  - **Network Pooled ($N = 306$):** Pooled mean surge is **+81.57 AQI points**, pooled median surge is **+80.38 AQI points**, and **85.95%** (263/306) of pairs elevated. Unweighted annual average is 86.83%.

---

## 5. Technical Environment & Automation Evaluation

### 5.1 Desktop Automation Constraints Encountered
As required by prompt Section 3 and Section 9, desktop automation was tested and evaluated:
1. **Windows User Interface Privilege Isolation (UIPI):** Power BI Desktop runs as an interactive Windows Store UWP application (`PBIDesktopStore.exe`) in User Session 1. Attempts by background automation processes to enumerate top-level windows via Win32 `EnumWindows` returned Win32 Error 5 (`ERROR_ACCESS_DENIED`), preventing simulated mouse/keystroke injection.
2. **Exclusive File Locking:** Power BI Desktop maintains an exclusive ReadWrite file handle on `D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis.pbix`. Direct file rewriting during an active desktop session triggers `System.IO.IOException: The process cannot access the file because it is being used by another process.`
3. **Absence of Headless CLI Compiler:** Power BI Desktop does not provide a command-line report compilation tool (`pbidesktop.exe /build`).

### 5.2 Resolution via Direct Analysis Services Tabular Querying
Rather than guessing or producing speculative documentation, the engine established a live TCP socket connection to Power BI Desktop's internal Analysis Services instance (`msmdsrv.exe`, port 50910). Using `Microsoft.PowerBI.AdomdClient.dll`:
- Discovered catalog GUID `2e9e0933-fbc0-486a-9963-ce244a48d6a0`.
- Verified that all 6 tables and 4 relationships are loaded into VertiPaq memory.
- Executed DAX queries evaluating all 21 measures in runtime.
- Automated this verification into `tests/test_powerbi_data.py` (`test_powerbi_live_analysis_services_dax`), ensuring continuous integration testing passes 100% (60/60 tests).

---

## 6. Report Design & Visual Implementation Blueprint

To complete visual formatting in Power BI Desktop with minimal user effort, the following assets have been delivered:

### 6.1 One-Click Dark Navy Theme
- **Asset:** `powerbi/theme_navy_environmental.json`
- **Application:** In Power BI Desktop ribbon: `View` $\to$ `Themes` dropdown $\to$ `Browse for themes` $\to$ select `powerbi/theme_navy_environmental.json`.
- **Palette Applied:** Primary Background (`#0B1220`), Card Surfaces (`#172438`), Primary Teal Accent (`#2DD4BF`), Cyan Accent (`#38BDF8`), Primary Text (`#F1F5F9`), Muted Text (`#A7B4C7`).

### 6.2 Three-Page Canvas Structure (1920 x 1080 Widescreen)

#### Page 1: Regional AQI Overview
- **Header:** Title: `Delhi-NCR Air Quality | Regional Overview`, Subtitle: `Monitoring coverage, pollution severity, and long-term AQI patterns · 2017–2023`.
- **KPI Row (Y: 100, Height: 120):**
  1. Card 1: `[Median AQI]` (199.29)
  2. Card 2: `[Data Completeness %]` (90.79%)
  3. Card 3: `[Severe AQI Days %]` (6.34%)
  4. Card 4: `[Sensor Capped Days %]` (12.44%)
- **Slicers (Top Right / Margin):** `dim_station[city]`, `dim_date[year]`, `dim_date[season]`.
- **Visuals:**
  - **Monthly Trend (Line Chart):** X-axis: `dim_date[year_month]`, Y-axis: `[Median AQI]`, `[Mean AQI]`.
  - **Category Donut:** Legend: `fact_daily_aqi[aqi_category]`, Values: `[Valid Station-Days]`.
  - **City Comparison (Bar Chart):** Y-axis: `dim_station[city]`, X-axis: `[Median AQI]`.
  - **Diurnal Line Chart:** X-axis: `agg_hourly_diurnal[hour_ist]`, Y-axis: `mean_aqi`, Legend: `is_winter`.

#### Page 2: Seasonal Inversion & Spatial Dynamics
- **Header:** Title: `Seasonal Dynamics | Winter Elevation & Spatial Differences`, Subtitle: `Comparing seasonal AQI distributions and monitoring locations across 2017–2023`.
- **KPI Row (Y: 100, Height: 120):**
  1. Card 1: `[Winter Median AQI]` (335.61)
  2. Card 2: `[Non-Winter Median AQI]` (154.00)
  3. Card 3: `[Winter Elevation Absolute]` (+181.61 pts)
  4. Card 4: `[Winter Elevation Ratio]` (2.18x)
- **Visuals:**
  - **City x Season Clustered Column Chart:** X-axis: `dim_station[city]`, Y-axis: `[Winter Median AQI]`, `[Non-Winter Median AQI]`.
  - **Season Distribution Bar Chart:** X-axis: `dim_date[season]`, Y-axis: `[Median AQI]`.
  - **Station Rankings (Two Tables):**
    - Top 10 Most Polluted: `dim_station[station_name]`, `dim_station[city]`, `[Valid Station-Days]`, `[Median AQI]` (Descending).
    - Bottom 10 Cleanest: `dim_station[station_name]`, `dim_station[city]`, `[Valid Station-Days]`, `[Median AQI]` (Ascending).
  - **Robustness Callout Textbox:** Details non-parametric Cliff's $d = 0.7637$, Moving Block Bootstrap 95% CI $[156.98, 202.14]$, and Tobit censoring coefficient $+154.17$ pts.

#### Page 3: Diwali Episode Analysis & Confounding
- **Header:** Title: `Diwali Episodes | Event Window & Seasonal Context`, Subtitle: `Station-matched AQI changes around verified festival dates · 2017–2023`.
- **KPI Row (Y: 100, Height: 120):**
  1. Card 1: `[Diwali Pooled Mean Surge]` (+81.57 pts)
  2. Card 2: `[Diwali Pooled Median Surge]` (+80.38 pts)
  3. Card 3: `[Diwali Station-Years Elevated %]` (85.95%)
  4. Card 4: `[Diwali Matched Station-Years]` (306)
- **Visuals:**
  - **Diwali Annual Surge Bar Chart:** X-axis: `dim_date[year]`, Y-axis: `[Diwali Pooled Mean Surge]`.
  - **October vs. November Cohort Matrix:** Rows: `dim_diwali_cohorts[timing_cohort]`, Values: `[Diwali Matched Station-Years]`, `[Diwali Pooled Mean Surge]`, `[Diwali Station-Years Elevated %]`.
  - **Causal Interpretation Callout:** "These results describe observed AQI patterns around Diwali. They do not independently establish that fireworks caused the observed changes. Seasonal pollution, meteorology, regional emissions, missing observations, and monitoring coverage may also contribute."

---

## 7. Sign-Off & Verification Status

| Component | Status | Verification Reference |
| :--- | :---: | :--- |
| **Data Source Parquet / CSVs** | Verified | 6 tables on disk in `data/processed/` |
| **Referential Integrity** | Verified | Zero orphan keys; 56 stations, 2,556 calendar dates |
| **VertiPaq Model Loading** | Verified | Active in `msmdsrv.exe` (PID 25716) |
| **DAX Measures Execution** | Verified | 21/21 measures executed via ADOMD.NET (Port 50910) |
| **Reconciliation Alignment** | Verified | 100% match with PostgreSQL and Streamlit outputs |
| **Automated Test Suite** | Verified | 60/60 tests passing in `tests/` (`14.15s`) |
| **Visual Theme Package** | Created | `powerbi/theme_navy_environmental.json` |
| **Interview Learning Guide** | Created | `docs/POWER_BI_FINAL_GUIDE.md` |

**Final Audit Verdict:** **STAGE 3 POWER BI DATA MODEL & DAX CALCULATIONS FULLY VALIDATED AND READY FOR PORTFOLIO DEMONSTRATION.**
