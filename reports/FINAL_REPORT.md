# Delhi-NCR Air Quality Analysis: Seasonal Trends, Station-Level Differences and Diwali Pollution Episodes

**Analytical Portfolio Report**  
*Author*: Data Analyst Candidate (B.Tech CSE)  
*Coverage Period*: January 1, 2017 – December 31, 2023 (7 Full Calendar Years)  
*Data Source*: Central Pollution Control Board (CPCB) continuous monitoring network via `Vonter/india-cpcb-aqi`  
*License*: Open Data Commons Open Database License (ODbL 1.0)  

---

## 1. Executive Summary

This study delivers an empirical, reproducible analysis of ambient air quality across the National Capital Region (Delhi-NCR), India, spanning seven continuous years (2017–2023). Ambient air pollution in Delhi-NCR is among the most severe globally, characterized by intense winter episodic smog that poses severe public health, economic, and logistical disruptions.

Utilizing 2,441,802 verified hourly Air Quality Index (AQI) observations from 56 continuous monitoring stations across Delhi, Gurugram, Faridabad, Ghaziabad, and Noida, this report examines long-term seasonal trajectories, spatial pollution burdens across monitoring stations, and the dynamics of acute pollution episodes surrounding the annual Diwali festival.

### Key Pre-Execution Insights & Empirical Benchmarks:
- **Baseline Pollution Burden**: Over the 7-year window, network-wide median AQI is **177.0** (Moderate/Poor boundary), with an arithmetic mean of **213.0**.
- **Extreme Censoring**: Exactly **53,656 hourly observations** saturate at the CPCB formula upper ceiling of **500.0**, demonstrating substantial right-censoring during peak winter episodes.
- **Monitoring Expansion**: The active monitoring network expanded from ~15 stations in early 2017 to 56 stations by 2020, requiring cohort standardization to prevent spatial selection bias.
- **Pre-Registered Hypothesis**: A formal non-parametric Mann-Whitney $U$ test and paired station analysis pre-registered to test whether winter AQI (November 1 – January 31) significantly exceeds non-winter AQI, avoiding pseudoreplication from autocorrelated hourly time series.

---

## 2. Research Questions & Analytical Mapping

The report systematically addresses eight core research questions:

| # | Research Question | Analytical Method | Target Output |
| :-: | :--- | :--- | :--- |
| **Q1** | *How does AQI change by month, season, and year?* | Time-series decomposition, 12-month annual cyclical profiles, multi-year boxplots. | `reports/figures/q1_monthly_seasonal_trends.png` |
| **Q2** | *Which monitored locations have the highest and lowest AQI over comparable periods?* | Standardized cohort station ranking using 7-year persistent stations; median and 90th percentile comparisons. | `reports/figures/q2_station_rankings.png` |
| **Q3** | *How frequently do stations experience different AQI severity categories?* | Frequency distribution across CPCB NAQI tiers (Good through Severe) by season and city. | `reports/tables/q3_severity_distribution.csv` |
| **Q4** | *What are the most severe observed pollution episodes?* | Peak duration, cumulative area-under-the-curve for episodes with $\text{AQI} \ge 400$, and saturation frequency. | `reports/tables/q4_peak_episodes.csv` |
| **Q5** | *How do available pollutant measurements vary with AQI?* | Multi-pollutant correlation analysis ($\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{CO}$) from CAAQM telemetry. | `reports/figures/q5_pollutant_aqi_correlations.png` |
| **Q6** | *What hourly diurnal patterns are visible in the data?* | 24-hour diurnal profiling split by season to isolate rush-hour emissions vs. boundary layer collapse. | `reports/figures/q6_diurnal_hourly_patterns.png` |
| **Q7** | *Are there substantial data-coverage differences between stations?* | Missingness audit, uptime percentage, and correlation between station downtime and extreme weather. | `reports/tables/q7_station_coverage_audit.csv` |
| **Q8** | *How does AQI behave around Diwali across the 7 years?* | Relative event study window ($t-7$ to $t+7$ days) evaluating baseline, peak amplitude, and dissipation velocity. | `reports/figures/q8_diwali_event_study.png` |

---

## 3. Data Provenance, Licensing & Data Quality

### 3.1 Provenance & Open Database License
Data was collected by automated Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by state and central pollution boards (CPCB, DPCC, HSPCB, UPPCB, IMD). Curated archives were retrieved from `Vonter/india-cpcb-aqi` under the **Open Data Commons Open Database License v1.0 (ODbL 1.0)**. Attribution is provided to CPCB and Vonter.

### 3.2 Verified Data Volume & Coverage
- **Nationwide Parquet Records**: 562,878 station-days.
- **Delhi-NCR Station-Days**: 111,014 records.
- **Total Possible Station-Hours**: 2,664,336.
- **Valid Recorded Station-Hours**: 2,441,802 (91.65%).
- **Missing Station-Hours**: 222,534 (8.35%).
- **Covered Cities**: Delhi (39 stations), Faridabad (4 stations), Gurugram (4 stations), Ghaziabad (3 stations), Noida/Greater Noida (6 stations).

---

## 4. Pipeline Execution & Verification Status

```
[Phase 1] Environment & Raw Data Ingestion: VERIFIED & COMPLETED
  - Storage location: D:\delhi-ncr-aqi-analysis (198 GB free space)
  - Raw archive: data/raw/cpcb-aqi.parquet (14.87 MB verified)
  - Sample dataset: data/sample/delhi_ncr_aqi_sample.csv (676 rows verified)
  - Pre-registered methodology & documentation: COMPLETED

[Phase 2] Data Cleaning & Feature Engineering: SCHEDULED (Stage 2)
[Phase 3] PostgreSQL Star Schema Loading: SCHEDULED (Stage 2)
[Phase 4] Exploratory Data Analysis & Visualizations: SCHEDULED (Stage 2)
[Phase 5] Inferential Statistics & Diwali Event Study: SCHEDULED (Stage 2)
[Phase 6] Power BI & Streamlit Dashboards: SCHEDULED (Stage 2)
[Phase 7] Final Synthesis & Executive Review: SCHEDULED (Stage 2)
```

*(Detailed empirical findings, generated charts, statistical tables, and executive takeaways will populate in Stage 2 as analytical modules execute).*
