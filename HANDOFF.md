# Session Handoff Document: Delhi-NCR Air Quality Analysis

**Project Name:** Delhi-NCR Air Quality Analysis: Seasonal Trends, Station-Level Differences, and Diwali Episodes  
**Project Root:** `D:\delhi-ncr-aqi-analysis`  
**Latest Backup Archive:** `D:\delhi-ncr-aqi-analysis-backups\stage-3-diwali-reconciliation-2026-10-22.zip`  
**Current State:** **Stage 3 Verified Complete, Reconciled & Fully Audited**  
**Local Environment:** Windows, Python 3.14.6 (`D:\anaconda3\python.exe`), PostgreSQL 18.0 (`delhi_aqi` on `D:\pg_tablespaces\delhi_aqi`), Streamlit 1.58.0 running at `http://localhost:8501`, Power BI Desktop installed, Git 2.49.0.

---

## 1. Context & Completed Work

### Stages 1 through 2C (Verified Complete & Audited)
- **Stage 1 (Commit `45697db`):** 562,878 raw records inspected; ODbL 1.0 license; directory structure; pre-registered methodology.
- **Stage 2A (Commit `1cdc92e`):** 2.66M hourly records cleaned; surrogate keys (`station_key`); dual timestamps (`timestamp_ist`, `timestamp_utc`); CPCB 500 ceiling flags.
- **Stage 2B (Commit `bf6d39a`):** PostgreSQL 18 Star Schema (`delhi_aqi` on `D:\pg_tablespaces\delhi_aqi`); 7 analytical CTE queries; 6 production EDA figures in `reports/figures/`.
- **Stage 2C (Commit `f1f4d97`):** Non-parametric hypothesis testing (Cliff's $d = 0.7637$); Moving Block Bootstrap ($L = 14$ days, 95% CI $[156.98, 202.14]$); Maximum Likelihood Tobit model (+154.17 pts); Station-matched Diwali causal decomposition. 36/36 unit tests passing.

### Stage 3 Reconciliation Milestones (Current Checkpoint)
- **Resolved Completeness Discrepancy (100.0% vs 90.79%):**
  - Root cause was pre-filtering denominator truncation: `filter_data(valid_only=True)` stripped invalid records before calling `compute_kpis()`, making `len(df) == len(valid_df)` (100,794 / 100,794 = 100%).
  - Fixed by capturing total scheduled records in active scope ($N_{total} = 111,014$) and passing `total_scheduled_days` to `compute_kpis()`. True data completeness of **90.79%** is now displayed.
- **Resolved Mean (215.44 vs 213.56) and IQR (187.4 vs 185.17) Discrepancy:**
  - Demonstrated that Mean = **215.44** and IQR = **187.40** are the exact municipal statistics of **Delhi City** alone ($N = 73,498$ station-days).
  - The authoritative **5-City Regional Network** benchmark is Mean = **213.56**, Median = **199.29**, and IQR = **185.17** ($N = 100,794$ station-days).
  - Added dynamic card titles in `dashboard/app.py` to prevent confusion between municipal scopes and the regional network.
- **Final Diwali Metric Reconciliation & Denominator Audit:**
  - Resolved discrepancy between preliminary draft table (+65.71 AQI surge, 84.82% elevated on 281 pairs) and live dashboard display (+81.57 AQI surge, 85.95% elevated on 306 pairs).
  - Traced exact data grain: daily station-level AQI; baseline window: $t-1$ (pre-Diwali eve); event window: $t+1$ (post-Diwali day); pairing unit: station-year pairs where `is_day_valid == TRUE` on both $t-1$ and $t+1$.
  - Demonstrated that the preliminary table used an exploratory subset with partial missingness dropped (leaving 30 pairs in 2018, 44 in 2021, and 46 in 2023; total 281). In contrast, the authoritative processed dataset `fact_daily_aqi.parquet` retains 40 in 2018, 55 in 2021, and 50 in 2023, yielding the full empirical **306 station-year pairs**.
  - Clarified denominator in UI: updated labels in `dashboard/app.py` from "Matched Station Pairs" $\to$ **"Matched Station-Year Pairs"** and "Stations Elevated" $\to$ **"Station-Years Elevated"**.
  - Verified defensive single-station case handling and confirmed presence of the 3-part causal confounding disclaimer (stubble burning, boundary layer collapse, sensor saturation).
- **Automated Testing:**
  - Added new unit test `test_diwali_single_station_filter` and extended `test_diwali_analysis_structure` in `tests/test_dashboard.py`.
  - **All 55 tests passing in 9.50s**.
- **Reconciliation Deliverables Updated:**
  - Section 8 added to `reports/DASHBOARD_KPI_RECONCILIATION.md`.
  - Section 5 and Master Matrix updated in `reports/DASHBOARD_VALIDATION_REPORT.md`.
  - `reports/FINAL_REPORT.md`, `docs/POWER_BI_DASHBOARD_GUIDE.md`, `docs/STREAMLIT_GUIDE.md`, and `docs/DASHBOARD_INTERVIEW_GUIDE.md` updated with authoritative figures.

---

## 2. Key Architectural Decisions to Preserve

1. **Storage Rules & C: Drive Protection:** Database tablespace and all large datasets remain pinned to `D:\pg_tablespaces\delhi_aqi` and `D:\delhi-ncr-aqi-analysis`. Never write large tables or dumps to `C:\`.
2. **Dual-Mode Data Sourcing:** Streamlit dashboard auto-detects PostgreSQL `localhost:5432`; if PostgreSQL is offline, it falls back seamlessly to Parquet files in `data/processed/`.
3. **Pure Function Separation:** All mathematical and visual data transformations in `dashboard/metrics.py` are pure functions, completely decoupled from Streamlit UI code for automated testing.
4. **Preserve Completeness Denominator:** Always compute completeness using total scheduled station-days in the active scope as the denominator, preventing validity pre-filters from collapsing completeness to 100%.
5. **Denominator Accuracy for Festival Events:** When pooling across 7 years, the unit of observation is station-year pairs ($N=306$), not unique monitoring stations ($N=56$).

---

## 3. How to Launch and Verify the Project

### Launch the Streamlit Dashboard:
```powershell
cd D:\delhi-ncr-aqi-analysis
D:\anaconda3\python.exe -m streamlit run dashboard/app.py
```
Open **`http://localhost:8501`** in any web browser.

### Run the Automated Test Suite:
```powershell
D:\anaconda3\python.exe -m pytest D:\delhi-ncr-aqi-analysis\tests -v
```
Output: **55 passed in 9.50s**.

---

## 2. Key Architectural Decisions to Preserve

1. **Storage Rules & C: Drive Protection:** Database tablespace and all large datasets remain pinned to `D:\pg_tablespaces\delhi_aqi` and `D:\delhi-ncr-aqi-analysis`. Never write large tables or dumps to `C:\`.
2. **Dual-Mode Data Sourcing:** Streamlit dashboard auto-detects PostgreSQL `localhost:5432`; if PostgreSQL is offline, it falls back seamlessly to Parquet files in `data/processed/`.
3. **Pure Function Separation:** All mathematical and visual data transformations in `dashboard/metrics.py` are pure functions, completely decoupled from Streamlit UI code for automated testing.
4. **Preserve Completeness Denominator:** Always compute completeness using total scheduled station-days in the active scope as the denominator, preventing validity pre-filters from collapsing completeness to 100%.

---

## 3. How to Launch and Verify the Project

### Launch the Streamlit Dashboard:
```powershell
cd D:\delhi-ncr-aqi-analysis
D:\anaconda3\python.exe -m streamlit run dashboard/app.py
```
Open **`http://localhost:8501`** in any web browser.

### Run the Automated Test Suite:
```powershell
D:\anaconda3\python.exe -m pytest D:\delhi-ncr-aqi-analysis\tests -v
```
Output: **54 passed in 20.65s**.
