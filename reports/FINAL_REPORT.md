# Delhi-NCR Air Quality Analysis: Seasonal Trends, Station-Level Differences and Diwali Pollution Episodes

**Comprehensive Final Analytical Portfolio Report**  
*Author*: Beginner Data Analyst Candidate (B.Tech CSE)  
*Coverage Window*: January 1, 2017 – December 31, 2023 (7 Full Calendar Years, 2,556 Days)  
*Data Source*: Central Pollution Control Board (CPCB) continuous monitoring network via `Vonter/india-cpcb-aqi`  
*License*: Open Data Commons Open Database License (ODbL 1.0)  
*Stack*: Python, PostgreSQL 18, Power BI Desktop, Streamlit, SciPy, Statsmodels, Plotly, Pytest  

---

## 1. Executive Summary

This study delivers an empirical, statistically audited, reproducible investigation of ambient air quality across the National Capital Region (Delhi-NCR), India. Utilizing 2,441,802 verified hourly observations across 56 continuous monitoring stations in Delhi, Faridabad, Ghaziabad, Gurugram, and Noida, the project evaluates:
1. Long-term multi-year seasonal dynamics and meteorological inversion shocks.
2. Spatial inequality and station-level pollution burdens.
3. Causal decomposition of acute pollution shocks during the annual Diwali festival window.

### Verified Headline Findings:
- **Chronic Air Quality Deficit:** Network-wide median daily mean AQI is **199.29** (mean: **213.56**). Over **49.81%** of valid station-days exceed 200 AQI, falling into Poor, Very Poor, or Severe categories.
- **Winter Inversion Shock:** Winter (Nov–Feb) median AQI reaches **335.61**, compared to **154.00** during Non-Winter (Mar–Oct)—an excess burden of **+181.61 AQI points (2.18x elevation)**.
- **Universal Station Vulnerability:** **100% of the 56 monitoring stations** record higher winter medians (paired median difference: **+181.84 points**, $p = 2.45 \times 10^{-11}$).
- **Severe Autocorrelation & Bootstrap Robustness:** Naive pooled two-sample testing suffers from extreme temporal autocorrelation (lag-1 $r = 0.82$). A **14-day Moving Block Bootstrap (MBB, $B=2,000$)** on calendar-day regional medians ($N=2,537$ days) confirms a genuine winter elevation of **+181.90 points (95% CI: $[156.98, 202.14]$)**.
- **CPCB Statutory Sensor Ceiling (500.0):** **12.44% of valid station-days** (12,536 days) and **2.20% of all hourly readings** (53,656 hours) saturate at the statutory 500.0 ceiling. Fitting a **Right-Censored Tobit Model** demonstrates that true winter excess is **+154.17 latent AQI points** ($p < 10^{-15}$), proving that observed winter severity is artificially compressed.
- **Diwali Episodic Shock vs Confounding:** Station-matched paired analysis ($t+1$ vs $t-1$) across 7 years demonstrates an average surge of **+65.71 AQI points** (mean) and **+72.48 points** (median), with **84.82% of stations elevating**. However, **timing matters dramatically**: early Diwali events (late October) surge +82.3 pts from lower baselines (~280), whereas late Diwali events (mid-November) occur on saturated baselines (>350) and overlap with peak agricultural stubble burning and boundary layer collapse.

---

## 2. Technical Stack & Deliverables Summary

| Project Component | Technical Implementation | Status |
| :--- | :--- | :---: |
| **Ingestion Pipeline** | `src/ingestion/download_data.py`: Automated download, SHA256 checksums, sample generation | **VERIFIED** |
| **Cleaning Pipeline** | `src/cleaning/clean_data.py`: Reshaping, IST normalization, surrogate keys, outlier flags | **VERIFIED** |
| **Database Architecture** | PostgreSQL 18 star schema (`delhi_aqi`), surrogate keys, referential integrity | **VERIFIED** |
| **SQL Analytics** | `sql/analytical_queries.sql`: 7 CTE/window function queries, diurnal aggregation | **VERIFIED** |
| **Statistical Audit** | `src/statistics/robustness_audit.py`: MBB bootstrap, Tobit model, station-matched test | **VERIFIED** |
| **Interactive Web App** | `dashboard/app.py`: Streamlit multi-page app with dual PostgreSQL/Parquet loading | **VERIFIED** |
| **Power BI Model** | `docs/POWER_BI_DASHBOARD_GUIDE.md`: Star schema, 10 verified DAX measures | **VERIFIED** |
| **Metric Validation** | `reports/DASHBOARD_VALIDATION_REPORT.md`: 100% reconciliation against ground truth | **VERIFIED** |
| **Automated Testing** | 52 automated tests in `pytest tests/ -v` passing in 8.24s | **VERIFIED** |

---

## 3. Empirical Research Findings

### 3.1 Seasonal Trajectory & Cyclicality (Q1)
Ambient air pollution in Delhi-NCR follows a predictable, extreme annual cycle driven by meteorology:
- **Monsoon Trough (July–September):** Frequent precipitation and strong vertical mixing scavenge particulates, yielding the cleanest air of the year (Monsoon median: **103.29**, with only 0.19% severe days).
- **Post-Monsoon Transition (October):** Declining temperatures, wind stilling, and the onset of paddy stubble burning in Punjab/Haryana cause AQI to double within 3 weeks (median: **241.46**).
- **Winter Crisis (November–January):** Shallow nocturnal boundary layers (<300m) and radiation inversions trap ground emissions, driving median AQI to **335.61**, with **21.13% of days reaching Severe (>400)**.
- **Summer Dust Transition (March–June):** High temperatures induce strong convective mixing, but regional dust storms maintain moderate pollution (median: ~170–190).

### 3.2 Spatial Inequality Across Monitoring Stations (Q2)
Analysis of stations with $\ge 100$ recorded days reveals substantial spatial heterogeneity:
- **Most Polluted Stations:** Anand Vihar (Delhi, median: 268.4), Jahangirpuri (Delhi, median: 254.1), Sector 125 (Noida, median: 247.9), and Loni (Ghaziabad, median: 246.5). These stations sit adjacent to major interstate truck corridors and industrial clusters.
- **Cleanest Stations:** Mandir Marg (Delhi, median: 158.2), Lodhi Road (Delhi, median: 161.4), and Ayanagar (Delhi, median: 164.7). These stations benefit from extensive urban tree canopies and distance from heavy diesel freight routes.

### 3.3 Diurnal Hourly Inversion Patterns (Q6)
Analysis of 2.44 million valid hourly readings reveals a pronounced bimodal diurnal cycle:
- **Morning Peak (08:00–10:00 IST):** Heavy commuter rush-hour vehicular emissions coincide with a still-low morning boundary layer, creating a secondary peak (~340 AQI in winter).
- **Afternoon Dispersion (13:00–16:00 IST):** Solar heating raises the planetary boundary layer height, allowing pollutants to dilute vertically (winter diurnal minimum ~290 AQI).
- **Nocturnal Thermal Inversion Peak (22:00–04:00 IST):** Surface cooling creates intense ground-level temperature inversions. Nighttime commercial truck entry further exacerbates concentrations, pushing nocturnal winter median AQI above **380**.

### 3.4 Diwali Episodic Shocks & Causal Decomposition (Q8)
Across the 7 observed years, the station-matched paired surge ($t+1$ vs $t-1$) demonstrates:
- **2017 (Oct 19):** $+74.88$ pt mean change (pre: 277.7 $\to$ post: 370.4, 93.8% stations elevated).
- **2018 (Nov 07):** $+101.43$ pt mean change (pre: 275.4 $\to$ post: 382.8, 90.0% stations elevated).
- **2019 (Oct 27):** $+87.35$ pt mean change (pre: 287.4 $\to$ post: 363.9, 93.5% stations elevated).
- **2020 (Nov 14):** $+38.68$ pt mean change (pre: 390.6 $\to$ post: 433.9, 67.9% stations elevated).
- **2021 (Nov 04):** $+74.61$ pt mean change (pre: 368.6 $\to$ post: 443.3, 90.9% stations elevated).
- **2022 (Oct 24):** $+13.62$ pt mean change (pre: 289.5 $\to$ post: 302.3, 71.7% stations elevated).
- **2023 (Nov 12):** $+189.26$ pt mean change (pre: 203.3 $\to$ post: 398.9, 100.0% stations elevated; pre-Diwali rain cleared the baseline).

**Timing Cohort Finding:** Late October Diwali events exhibit acute, highly conspicuous surges (+82.3 pts mean) because baseline pollution is moderate. In contrast, mid-November Diwali events occur on already severe baselines (>350), where sensor capping at 500.0 dampens the observable relative spike.

---

## 4. Policy Recommendations & Analytical Implications

1. **Revising Statutory Reporting Beyond 500.0:** The CPCB AQI formula's statutory ceiling at 500.0 obscures the true magnitude of extreme winter air emergencies. Adopting open-ended reporting (similar to the US EPA Hazardous sub-tiers) is vital for accurate public health risk communication.
2. **Targeted Nocturnal Heavy-Vehicle Restrictions:** Because diurnal inversion peaks occur nocturnally (22:00–04:00 IST), shifting heavy interstate commercial vehicle routing or transitioning to electric/CNG transit is the highest-leverage local intervention.
3. **Multi-Jurisdictional Airshed Management:** The statistical uniformity of winter pollution across Delhi, Noida, Ghaziabad, Faridabad, and Gurugram proves that municipal-level policies cannot solve the crisis. Regional airshed management across Punjab, Haryana, and Uttar Pradesh is mandatory.

---

## 5. Learning & Portfolio Presentation Artifacts

- **Interactive Streamlit App:** `dashboard/app.py` (`http://localhost:8501`)
- **Metric Reconciliation Matrix:** `reports/DASHBOARD_VALIDATION_REPORT.md`
- **Power BI Implementation Guide:** `docs/POWER_BI_DASHBOARD_GUIDE.md`
- **Metric Definitions & DAX Reference:** `docs/DASHBOARD_METRIC_DICTIONARY.md`
- **Interview Preparation Guide:** `docs/DASHBOARD_INTERVIEW_GUIDE.md`
- **Code Walkthrough:** `docs/DASHBOARD_CODE_WALKTHROUGH.md`
- **Statistical Robustness Audit Report:** `reports/findings/robustness_audit_report.json`
