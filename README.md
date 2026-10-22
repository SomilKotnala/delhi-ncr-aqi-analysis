# Delhi-NCR Air Quality Analysis: Seasonal Trends, Station-Level Differences, and Diwali Pollution Episodes

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2018-336791.svg)](https://www.postgresql.org/)
[![BI Tool](https://img.shields.io/badge/BI-Power%20BI%20Desktop-f2c811.svg)](https://powerbi.microsoft.com/)
[![License: ODbL](https://img.shields.io/badge/License-ODbL%201.0-brightgreen.svg)](https://opendatacommons.org/licenses/odbl/1.0/)
[![Data Source](https://img.shields.io/badge/Source-CPCB%20India-orange.svg)](https://airquality.cpcb.gov.in/AQI_India/)

An end-to-end, reproducible Data Analytics portfolio project investigating 7 full years (2017–2023) of ambient Air Quality Index (AQI) dynamics across 56 continuous monitoring stations in the Delhi National Capital Region (Delhi, Gurugram, Faridabad, Ghaziabad, and Noida).

---

## 1. Project Highlights & Empirical Dataset Scope

- **Real Continuous Monitoring**: Sourced from official Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by CPCB, DPCC, HSPCB, UPPCB, and IMD.
- **Multi-Year Horizon**: **2017-01-01 through 2023-12-31** (7 full calendar years, covering 7 consecutive Diwali festival windows).
- **Network Scale**: **56 unique stations** across 5 cities in Delhi-NCR (Delhi: 39, Faridabad: 4, Gurugram: 4, Ghaziabad: 3, Noida/Greater Noida: 6).
- **Data Volume**: **111,014 station-day records** representing **2,441,802 valid hourly observations** (91.65% network completeness).
- **Analytical Rigor**:
  - Pre-registered non-parametric statistical hypothesis testing (Mann-Whitney U, Cliff's delta, bootstrap CIs).
  - Explicit avoidance of pseudoreplication by aggregating autocorrelated hourly time series into station-day units.
  - Transparent handling of the **500 AQI sensor ceiling** (53,656 capped observations).
  - Kimball Star Schema implemented in **PostgreSQL 18** with advanced CTEs and window functions.
  - Interactive **Power BI Desktop** report with custom DAX measures and normalized event studies.

### Authoritative Key Findings:
- **Baseline Regional AQI:** Median **199.29**, Mean **213.56**, IQR **185.17** across 100,794 valid station-days (90.79% data completeness out of 111,014 scheduled station-days).
- **Winter Elevation:** Winter median **335.61** vs Non-Winter median **154.00** ($\mathbf{+181.61}$ pts absolute elevation, $\mathbf{2.18\times}$ ratio).
- **Diwali Festival Surge:** Network pooled mean paired surge of $\mathbf{+81.57}$ AQI points (median $\mathbf{+80.38}$ pts) across **306 station-year pairs**, with **85.95%** (263/306) of station-years elevating.
  - *Verified Annual Breakdown ($N=306$):* 2017: 16 | 2018: **40** | 2019: 46 | 2020: 53 | 2021: 55 | 2022: 46 | 2023: **50**.
  - *(Note on Historical Typo: 2023 having 60 pairs is physically impossible as the entire network comprises 56 stations in total; 2023 has 50 valid pairs. 2018 having 30 pairs was from an exploratory draft that dropped partial-missingness stations; official statutory standard preserves 40 valid pairs).*
- **Timing Cohorts:** October Diwali (2017, 2019, 2022 — 108 pairs) pooled surge **+58.92 pts** vs November Diwali (2018, 2020, 2021, 2023 — 198 pairs) pooled surge **+93.92 pts**.

### Known Methodological Limitations:
1. **Instrument Sensor Ceiling Truncation:** Continuous analyzers cap PM2.5 and AQI calculations at 500.0, truncating extreme peaks and compressing observable relative surges during peak winter episodes (12.44% of station-days affected).
2. **Meteorological & Seasonal Confounding:** Post-monsoon agricultural burning in Punjab/Haryana and planetary boundary layer height collapse co-occur with Diwali, requiring careful counterfactual interpretation rather than naive 100% fireworks attribution.
3. **Network Expansion Across Time:** Network active stations grew from 17 in 2017 to 56 in 2021–2023; cross-year comparisons control for station fixed effects through paired differences.

---

## 2. Repository Architecture

```
delhi-ncr-aqi-analysis/
├── data/
│   ├── raw/                      # Immutable raw parquet data (excluded from git)
│   ├── processed/                # Normalized analytical tables (fact & dimension tables)
│   └── sample/                   # Stratified 676-row sample CSV (committed for testing)
├── notebooks/                    # Exploratory and prototyping Jupyter notebooks
├── src/                          # Modular production Python code
│   ├── ingestion/                # Automated download and integrity checking
│   ├── cleaning/                 # Wide-to-long reshaping, typing, outlier flags
│   ├── analysis/                 # Seasonal trends, station rankings, diurnal patterns
│   ├── statistics/               # Non-parametric tests, Cliff's delta, bootstrap CIs
│   └── database/                 # PostgreSQL loading & schema migrations
├── sql/                          # DDL schemas, indexing strategies, analytical queries
├── tests/                        # Automated pytest suites for transforms and schemas
├── reports/
│   ├── figures/                  # Publication-grade charts with source attribution
│   ├── tables/                   # Summary CSV tables
│   └── findings/                 # Pre-computed key metrics for dashboard & report
├── dashboard/                    # Power BI specifications, DAX scripts, Streamlit app
├── docs/                         # Comprehensive learning and interview guides
│   ├── LEARNING_GUIDE.md         # Step-by-step beginner study roadmap & glossary
│   ├── CODE_WALKTHROUGH.md       # Architectural deep-dive & code explanations
│   ├── SQL_LEARNING_GUIDE.md     # PostgreSQL setup, Star Schema, CTEs, Window functions
│   ├── STATISTICS_LEARNING_GUIDE.md # Parametric vs Non-parametric, Pseudoreplication
│   ├── INTERVIEW_PREPARATION.md  # 60s pitch, technical interview Q&A, viva defense
│   └── POWER_BI_DASHBOARD_GUIDE.md # Multi-page report layout & step-by-step build guide
├── DATA_SOURCES_AND_LICENSES.md  # Attribution, ODbL 1.0 terms, data provenance
├── PROJECT_METHODOLOGY.md        # Pre-registered hypothesis & Diwali event study framework
├── DATA_DICTIONARY.md            # Schema definitions & official CPCB AQI breakpoints
├── LIMITATIONS.md                # Instrument capping, network expansion, confounders
├── requirements.txt              # Pinned Python package dependencies
└── README.md                     # Project overview and run instructions
```

---

## 3. Quickstart & Reproducibility Guide

### Step 1: Clone or Navigate to the Project
```bash
cd D:/delhi-ncr-aqi-analysis
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Ingestion & Verify Integrity
To download the verified CPCB Parquet dataset (~14.87 MB) into `data/raw/` and regenerate the stratified sample:
```bash
python src/ingestion/download_data.py
```

### Step 4: Run the Interactive Streamlit Dashboard
Launch the local web application with instant dual PostgreSQL / Parquet loading:
```bash
python -m streamlit run dashboard/app.py
```
Open **`http://localhost:8501`** to interact with the 3 analytical tabs, dynamic slicers, and CPCB risk distributions.

### Step 5: Run Automated Tests
Verify all 61 unit and integration tests covering cleaning, database, statistics, dashboard metrics, and Power BI DAX runtime:
```bash
python -m pytest tests/ -v
```

### Step 6: Power BI Desktop Model & Executive Dashboard
The production Power BI report is packaged as both a native developer project and a signed binary deliverable:
- **Final Power BI File:** [`delhi_ncr_aqi_analysis_final.pbix`](delhi_ncr_aqi_analysis_final.pbix)
- **Native PBIP Project:** [`delhi_ncr_aqi_analysis_native.pbip`](delhi_ncr_aqi_analysis_native.pbip)
- **Visual Structure:** 3 pages, 34 visual containers across Dark Navy Environmental aesthetic (`#0B1220`, `#111C2E`, `#172438`).
- **DAX Measures:** 22 production measures verified against active Tabular Engine (`msmdsrv.exe`).
- **Page Layout:**
  1. *Regional AQI Overview* (11 visuals: KPI callout cards, 84-month chronological trend, CPCB category donut with white center value, municipal rankings, 24-hr diurnal cycle).
  2. *Seasonal Dynamics & Spatial Inversion* (12 visuals: 2.18x winter-to-non-winter contrast, Top 10 polluted vs cleanest stations, Tobit censoring methodology panel).
  3. *Diwali Episode Analysis & Confounding* (11 visuals: +81.57 pt paired surge across 306 station-years, October vs November timing cohorts, annual surge breakdown, causal deconfounding panel).

### Step 7: Explore the Comprehensive Documentation
- [`docs/DASHBOARD_METRIC_DICTIONARY.md`](docs/DASHBOARD_METRIC_DICTIONARY.md): Complete metric definitions, formulas, and DAX/SQL logic.
- [`reports/DASHBOARD_VALIDATION_REPORT.md`](reports/DASHBOARD_VALIDATION_REPORT.md): Metric reconciliation audit (100% verified against benchmarks).
- [`docs/DASHBOARD_INTERVIEW_GUIDE.md`](docs/DASHBOARD_INTERVIEW_GUIDE.md): 15 high-yield interview questions with model STAR answers.
- [`docs/DASHBOARD_CODE_WALKTHROUGH.md`](docs/DASHBOARD_CODE_WALKTHROUGH.md): Beginner-friendly code explanations of `data_access.py`, `metrics.py`, and `app.py`.
- [`docs/STREAMLIT_GUIDE.md`](docs/STREAMLIT_GUIDE.md): Architecture, caching, and troubleshooting guide.
- [`PROJECT_METHODOLOGY.md`](PROJECT_METHODOLOGY.md): Pre-registered hypotheses and Diwali event study framework.
- [`LIMITATIONS.md`](LIMITATIONS.md): Instrument capping, network expansion, and meteorological confounders.

---

## 4. Primary Stack & Tools Used

| Tool / Library | Role in Project | Cost |
| :--- | :--- | :---: |
| **Python 3.12 / 3.14** | Core programming language for data pipeline | ₹0 (Open Source) |
| **Pandas & PyArrow** | Ingestion, columnar storage, wide-to-long reshaping | ₹0 (Open Source) |
| **SciPy & Statsmodels** | Mann-Whitney U, Cliff's delta, bootstrap confidence intervals | ₹0 (Open Source) |
| **PostgreSQL 18 & pgAdmin 4** | Relational Star Schema, analytical CTEs, window functions | ₹0 (Open Source) |
| **Power BI Desktop** | Multi-page executive BI dashboard with custom DAX measures | ₹0 (Free Tier) |
| **Streamlit** | Supplementary local interactive exploration tool | ₹0 (Open Source) |
| **Git & GitHub** | Version control, documentation, portfolio presentation | ₹0 (Free Tier) |

---

## 5. Licensing & Data Attribution

- **Database License**: [Open Data Commons Open Database License v1.0 (ODbL 1.0)](https://opendatacommons.org/licenses/odbl/1.0/).
- **Data Source**: Continuous Ambient Air Quality Monitoring Network, **Central Pollution Control Board (CPCB)**, Ministry of Environment, Forest and Climate Change, Government of India.
- **Curated Archive**: Maintained by [Vonter/india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi).
