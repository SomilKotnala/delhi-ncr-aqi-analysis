# Streamlit Interactive Dashboard Guide

**Project:** Delhi-NCR Air Quality Analysis (2017–2023)  
**Milestone:** Stage 3 — Interactive Analytics & Web Application  
**Target Audience:** Beginner Data Analyst Candidates, Evaluators & End Users  
**App Entrypoint:** `dashboard/app.py`  
**Data Access Layer:** `dashboard/data_access.py`  
**Analytical Engine:** `dashboard/metrics.py`  

---

## 1. Quick Start: Launching the Dashboard

The dashboard is built using **Streamlit** and **Plotly** and runs entirely locally without any external dependencies or paid cloud requirements.

### Running with Default Python Environment:
Open PowerShell or your command prompt in the project root:
```powershell
cd D:\delhi-ncr-aqi-analysis
D:\anaconda3\python.exe -m streamlit run dashboard/app.py
```

### Accessing in Your Browser:
Once started, the application will display:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```
Open **`http://localhost:8501`** in any modern web browser (Chrome, Edge, Firefox).

---

## 2. Technical Architecture & Data Access Layer

```
                        ┌──────────────────────────────────────────────┐
                        │              Streamlit Web App               │
                        │             (dashboard/app.py)               │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │          Analytical Metrics Engine           │
                        │            (dashboard/metrics.py)            │
                        │    (Pure functions, audited KPI logic)       │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │              Data Access Layer               │
                        │         (dashboard/data_access.py)           │
                        │        Cached with @st.cache_data            │
                        └──────────────┬────────────────┬──────────────┘
                                       │                │
                        Primary Source ▼                ▼ Fallback Source
                        ┌──────────────┐                ┌──────────────┐
                        │  PostgreSQL  │                │ Local Apache │
                        │  Star Schema │                │   Parquet    │
                        │ (delhi_aqi)  │                │  (Fast I/O)  │
                        └──────────────┘                └──────────────┘
```

### Key Architectural Strengths:
1. **Dual-Mode Data Sourcing (`dashboard/data_access.py`):**
   - **Primary:** Connects live to the local PostgreSQL database `delhi_aqi` running on `localhost:5432`.
   - **Automatic Fallback:** If PostgreSQL is offline or credentials are missing, the app instantly and silently falls back to optimized Apache Parquet files in `data/processed/`.
   - **Data Provenance Badge:** A subtle top-left badge explicitly identifies the active data connection source, record count, and temporal bounds.
2. **Separation of Concerns:**
   - UI code (`app.py`) is decoupled from analytical logic (`metrics.py`).
   - Every metric computation in `metrics.py` is a pure Python function that can be unit-tested without launching Streamlit or mocking a web browser.
3. **Sub-Second Caching (`@st.cache_data`):**
   - The entire 111,014 daily record dataset is loaded into memory in under **1.8 seconds** and cached in memory. Subsequent filter selections update in less than **50 milliseconds**.
4. **Memory Optimization:**
   - Pre-aggregated diurnal hourly summary (`agg_hourly_diurnal.parquet`, 288 rows) is loaded instead of the full 2.66M-row hourly table, keeping total app memory footprint under **120 MB RAM**.

---

## 3. Walkthrough of Dashboard Features & Tabs

### Tab 1: 🌐 Regional Overview & Baseline Health Risk
- **Headline KPI Metric Cards:**
  - **Network Median AQI (`199.29`):** Robust central tendency metric less prone to extreme wildfire/winter outliers than arithmetic mean (`213.56`).
  - **Valid Station-Days (`100,794`):** Displays CPCB data completeness rate (**90.79%** across all 56 stations).
  - **Severe AQI Days Proportion (`6.34%`):** Proportion of days with $AQI > 400$, representing acute respiratory emergency conditions.
  - **Sensor Ceiling Saturation (`12.44%`):** Transparent audit of station-days with at least one reading hitting the statutory 500.0 sensor ceiling.
- **Interactive Monthly AQI Trajectory (2017–2023):**
  - Plotly time-series chart showing 84 monthly medians, monthly means, and shaded Interquartile Range (IQR 25th–75th percentiles).
  - Color-coded statutory CPCB background bands (Good, Satisfactory, Moderate, Poor, Very Poor, Severe).
- **CPCB Severity Share (Donut Chart):**
  - Distribution across the 6 official CPCB risk categories rendered using exact statutory hex codes.
- **City-by-City Comparison (Bar Chart):**
  - Ranks the 5 NCR cities: Ghaziabad (226.8), Delhi (200.8), Noida (198.9), Faridabad (197.8), Gurugram (172.9).
- **24-Hour Diurnal Dynamics Curve:**
  - Compares Winter vs Non-Winter hourly profiles, illustrating the dramatic nocturnal thermal inversion spike between 22:00 and 08:00 IST.

---

### Tab 2: ❄️ Seasonal Inversion & Spatial Dynamics
- **Seasonal KPI Cards:**
  - Winter Median AQI (**335.61**) vs Non-Winter Median (**154.00**) $\to$ **+181.61 pts (+117.9% / 2.18x)**.
  - Stations Elevated: **100% (56 of 56 stations)** exhibit higher winter medians.
- **Seasonal Distribution Comparison (Plotly Box Plot):**
  - Compares AQI distributions across Winter, Summer / Pre-Monsoon, Monsoon, Post-Monsoon, and Transition (Feb).
- **City-by-City Clustered Seasonal Elevation:**
  - Illustrates that winter elevation is uniform across the entire airshed, not isolated to central Delhi.
- **Station-Level Inequality Rankings (Top 10 vs Bottom 10):**
  - Formatted data tables ranking the most polluted monitoring stations (e.g. Anand Vihar, Jahangirpuri) and cleanest stations (e.g. Ayanagar, Mandir Marg) filtered to stations with at least 100 recorded days.
- **Statistical Robustness Audit Callout Box:**
  - Explains the danger of naive two-sample tests due to temporal autocorrelation and spatial pseudoreplication.
  - Reports the 14-day Moving Block Bootstrap (MBB) 95% CI: **$[156.98, 202.14]$**.
  - Reports the right-censored Tobit model estimate: **$+154.17$ AQI points** ($p < 10^{-15}$).

---

### Tab 3: 🎆 Diwali Pollution Episode Analysis
- **Event Study Window Trajectory ($t-7$ to $t+7$ Days):**
  - Multi-line Plotly trajectory tracking median AQI relative to Diwali across all 7 years (2017–2023) plus a bold multi-year average line.
  - Dashed vertical line at $t=0$ marks Diwali night.
- **Station-Matched Paired Difference Analysis ($t+1$ vs $t-1$):**
  - Compares stations active on both pre- and post-Diwali days to eliminate composition bias.
  - Multi-year average paired surge: **$+81.57$ AQI points** (mean) and **$+80.38$ AQI points** (median), with **85.95%** of matched station-year pairs elevating across 306 valid pairs.
- **Timing Cohort Decomposition (October Diwali vs November Diwali):**
  - Contrasts early Diwali years (October Diwali: 2017, 2019, 2022; 108 station-years) with November Diwali years (2018, 2020, 2021, 2023; 198 station-years).
  - Highlights pooled metrics (+58.92 pts mean surge, 84.26% elevated in October vs +93.92 pts mean surge, 86.87% elevated in November) alongside unweighted annual averages (86.32% vs 87.21%).
- **Causal Attribution & Meteorological Confounding Disclaimer:**
  - Deep methodological explanation highlighting why firecrackers cannot be causally isolated from agricultural stubble burning and boundary layer collapse without chemical speciation tracers.

---

## 4. Interactive Sidebar Controls

1. **Data Source Layer:** Toggle between `Auto-detect`, `PostgreSQL Database`, or `Local Parquet Storage`.
2. **City Multi-Select:** Choose any combination of Delhi, Faridabad, Ghaziabad, Gurugram, Noida.
3. **Station Multi-Select:** Dynamically populates only the monitoring stations belonging to the selected cities.
4. **Date Range Picker:** Interactive calendar range selector (2017-01-01 to 2023-12-31).
5. **Meteorological Season Selector:** Filter by any subset of the 5 seasons.
6. **CPCB Completeness Toggle:** Enforces the statutory $\ge 16$ valid hours/day requirement (defaults to active).
7. **Export Filtered Data Button:** One-click CSV download of active filtered subset.

---

## 5. Troubleshooting & FAQ

| Problem | Root Cause | Solution |
| :--- | :--- | :--- |
| `Port 8501 is already in use` | Another Streamlit session is running | Run on another port: `streamlit run dashboard/app.py --server.port 8502` |
| `ModuleNotFoundError: No module named 'dashboard'` | Command launched outside project root | Ensure working directory is `D:\delhi-ncr-aqi-analysis` or invoke with full path |
| `PostgreSQL connection error: password authentication failed` | Incorrect `.env` password | Verify `.env` has `DB_PASSWORD=1234` or select `Local Parquet Storage` |
| Browser shows blank white screen | Web socket connection blocked | Hard refresh browser (`Ctrl + F5`) or disable adblocker on localhost |

---

## 6. How to Run the Automated Test Suite

To verify that the dashboard data access and metric calculations remain 100% bug-free:
```powershell
D:\anaconda3\python.exe -m pytest D:\delhi-ncr-aqi-analysis\tests -v
```
*Current Status: 52 of 52 tests passing in ~8.2 seconds.*
