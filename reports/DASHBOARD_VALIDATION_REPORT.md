# Dashboard Metric Validation & Reconciliation Report

**Project:** Delhi-NCR Air Quality Analysis  
**Milestone:** Stage 3 — Interactive Dashboard Validation  
**Date of Audit:** October 22, 2026  
**Auditor:** Lead Analytical AI Agent  
**Environment:** Python 3.14.6, PostgreSQL 18.0 (localhost:5432 / delhi_aqi), Streamlit 1.58.0, Power BI Desktop  

---

## 1. Executive Summary

This validation audit reconciles all headline analytical metrics, categorical proportions, and statistical findings displayed across the **Streamlit Interactive Dashboard** (`dashboard/app.py`) and specified for the **Power BI Desktop Report Model** (`docs/POWER_BI_DASHBOARD_GUIDE.md`) against ground-truth benchmarks established during the Stage 2B PostgreSQL integration and Stage 2C Statistical Robustness Audit.

Every metric was independently calculated through three distinct analytical pipelines:
1. **SQL Ground Truth:** Executed directly against the PostgreSQL star-schema tables (`delhi_aqi` on `D:\pg_tablespaces\delhi_aqi`).
2. **Python / Pandas Analytical Engine:** Executed via `dashboard/metrics.py` on the verified `fact_daily_aqi.parquet` dataset.
3. **Automated Unit Tests:** Verified via `pytest tests/test_dashboard.py` (52 passed in 8.24s).

**Audit Verdict:** **100% RECONCILIATION PASSED.** There are zero discrepancies between the SQL ground truth and the Python / Streamlit calculation engine.

---

## 2. Metric Reconciliation Master Matrix

| # | Metric Identifier | Business Definition & Grain | SQL Reference Query Output | Python / Dashboard Metric | DAX Benchmark Formula | Status |
| :- | :--- | :--- | :--- | :--- | :--- | :---: |
| **M1** | **Network Median AQI** | Median `daily_mean_aqi` across valid station-days | `199.29` | `199.29` | `MEDIAN(FactDailyAQI[daily_mean_aqi])` | **PASS** |
| **M2** | **Network Mean AQI** | Arithmetic mean of `daily_mean_aqi` across valid station-days | `213.56` | `213.56` | `AVERAGE(FactDailyAQI[daily_mean_aqi])` | **PASS** |
| **M3** | **Valid Station-Days** | Total records satisfying CPCB $\ge 16$ valid hours/day | `100,794` | `100,794` | `CALCULATE(COUNTROWS(FactDailyAQI), FactDailyAQI[is_day_valid] = TRUE())` | **PASS** |
| **M4** | **Total Scheduled Station-Days** | Total station-days across 56 stations (2017–2023) | `111,014` | `111,014` | `COUNTROWS(FactDailyAQI)` | **PASS** |
| **M5** | **Data Completeness %** | Proportion of scheduled days meeting CPCB validity | `90.79%` | `90.79%` | `DIVIDE([Valid Station Days], [Total Station Days], 0)` | **PASS** |
| **M6** | **Severe AQI Days Count** | Valid station-days where `daily_mean_aqi > 400.0` | `6,389` | `6,389` | `CALCULATE(COUNTROWS(...), FactDailyAQI[daily_mean_aqi] > 400)` | **PASS** |
| **M7** | **Severe AQI Days %** | Percentage of valid days in Severe category | `6.34%` | `6.34%` | `DIVIDE([Severe Station Days], [Valid Station Days], 0)` | **PASS** |
| **M8** | **Sensor Capped Days Count** | Valid station-days with $\ge 1$ hourly reading hitting 500.0 | `12,536` | `12,536` | `CALCULATE(COUNTROWS(...), FactDailyAQI[capped_hours_count] > 0)` | **PASS** |
| **M9** | **Sensor Capped Days %** | Percentage of valid days with sensor saturation | `12.44%` | `12.44%` | `DIVIDE([Capped Days Count], [Valid Station Days], 0)` | **PASS** |
| **M10** | **Winter Median AQI** | Median AQI during winter months (Nov, Dec, Jan, Feb) | `335.61` | `335.61` | `CALCULATE([Median AQI], FactDailyAQI[is_winter] = TRUE())` | **PASS** |
| **M11** | **Non-Winter Median AQI** | Median AQI during non-winter months (Mar–Oct) | `154.00` | `154.00` | `CALCULATE([Median AQI], FactDailyAQI[is_winter] = FALSE())` | **PASS** |
| **M12** | **Winter Elevation** | Absolute median difference (Winter − Non-Winter) | `+181.61` | `+181.61` | `[Winter Median AQI] - [Non-Winter Median AQI]` | **PASS** |
| **M13** | **Winter Elevation Ratio** | Multiplicative ratio (Winter / Non-Winter) | `2.18x` | `2.18x` | `DIVIDE([Winter Median AQI], [Non-Winter Median AQI], 0)` | **PASS** |
| **M14** | **Winter Stations Elevated** | Proportion of stations with higher winter median | `100.0% (56/56)` | `100.0% (56/56)` | `1.00` | **PASS** |
| **M15** | **Moving Block Bootstrap 95% CI** | 14-day temporal block bootstrap median elevation ($N=2,537$ cal days) | `[156.98, 202.14]` | `[156.98, 202.14]` | N/A (Statistical Robustness Card) | **PASS** |
| **M16** | **Right-Censored Tobit Coeff** | Latent winter pollution effect accounting for 500 ceiling | `+154.17 pts` | `+154.17 pts` | N/A (Statistical Robustness Card) | **PASS** |
| **M17** | **Diwali 7-Year Paired Mean Surge** | Matched station-year difference ($t+1$ vs $t-1$) across 306 pairs | `+81.57` | `+81.57` | N/A (Event Study Decomposition) | **PASS** |
| **M18** | **Diwali 7-Year Paired Median Surge** | Matched station-year difference ($t+1$ vs $t-1$) across 306 pairs | `+80.38` | `+80.38` | N/A (Event Study Decomposition) | **PASS** |
| **M19** | **Diwali Station-Years Elevated %** | Proportion of matched station-year pairs showing post-Diwali spike | `85.95%` | `85.95%` | N/A (Event Study Decomposition) | **PASS** |

---

## 3. CPCB Categorical Distribution Reconciliation

The table below reconciles the distribution of station-days across the 6 statutory CPCB categories:

| CPCB Category | AQI Range | Color Hex | Valid Station-Days | Percentage (%) | Cumulative % | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Good** | $0 - 50$ | `#00B050` | 2,126 | 2.11% | 2.11% | **MATCH** |
| **Satisfactory** | $51 - 100$ | `#92D050` | 16,983 | 16.85% | 18.96% | **MATCH** |
| **Moderate** | $101 - 200$ | `#E6B800` | 31,478 | 31.23% | 50.19% | **MATCH** |
| **Poor** | $201 - 300$ | `#FF8C00` | 24,797 | 24.60% | 74.79% | **MATCH** |
| **Very Poor** | $301 - 400$ | `#E60000` | 19,021 | 18.87% | 93.66% | **MATCH** |
| **Severe** | $401 - 500+$ | `#7A0019` | 6,389 | 6.34% | 100.00% | **MATCH** |
| **Total Valid** | **—** | **—** | **100,794** | **100.00%** | **100.00%** | **MATCH** |

**Analytical Takeaway:** Over **49.81%** of all valid recorded station-days exceed 200 AQI (falling into Poor, Very Poor, or Severe), demonstrating persistent chronic air pollution across Delhi-NCR.

---

## 4. City-by-City Reconciliation

Reconciliation of city-level aggregations across all 5 reported NCR cities:

| City | Valid Station-Days | Total Stations | Median AQI | Mean AQI | Severe Days % | Capped Days % | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Ghaziabad** | 5,518 | 3 | **212.07** | 222.05 | 7.61% | 15.15% | **MATCH** |
| **Delhi** | 73,498 | 39 | **201.83** | 215.44 | 6.73% | 12.59% | **MATCH** |
| **Noida** | 10,517 | 6 | **193.88** | 211.21 | 6.15% | 10.75% | **MATCH** |
| **Faridabad** | 5,348 | 4 | **188.04** | 204.07 | 4.73% | 15.11% | **MATCH** |
| **Gurugram** | 5,913 | 4 | **183.10** | 195.11 | 2.06% | 8.52% | **MATCH** |
| **Total / Network** | **100,794** | **56** | **199.29** | **213.56** | **6.34%** | **12.44%** | **MATCH** |

---

## 5. Diwali Event Study Reconciliation (2017–2023)

Detailed reconciliation of the station-matched paired difference analysis ($t+1$ post-Diwali vs $t-1$ pre-Diwali):

### 5.1 Authoritative 7-Year Paired Reconciliation Table

| Year | Diwali Date | Timing Cohort | Matched Station-Year Pairs | Pre-Diwali Median ($t-1$) | Post-Diwali Median ($t+1$) | Mean Paired Surge | Median Paired Surge | Station-Years Elevated (%) | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2017** | 2017-10-19 | October Diwali | 16 | 311.32 | 418.91 | +103.49 | +94.25 | 93.75% | **MATCH** |
| **2018** | 2018-11-07 | November Diwali | 40 | 316.50 | 398.05 | +75.86 | +95.71 | 90.00% | **MATCH** |
| **2019** | 2019-10-27 | October Diwali | 46 | 303.64 | 386.52 | +82.82 | +89.85 | 93.48% | **MATCH** |
| **2020** | 2020-11-14 | November Diwali | 53 | 345.92 | 381.54 | +27.56 | +31.83 | 67.92% | **MATCH** |
| **2021** | 2021-11-04 | November Diwali | 55 | 332.79 | 400.71 | +77.39 | +78.25 | 90.91% | **MATCH** |
| **2022** | 2022-10-24 | October Diwali | 46 | 282.83 | 297.33 | +19.51 | +10.52 | 71.74% | **MATCH** |
| **2023** | 2023-11-12 | November Diwali | 50 | 180.08 | 392.11 | +196.90 | +198.17 | 100.00% | **MATCH** |
| **Combined** | **—** | **7 Years** | **306** | **303.64** | **392.11** | **+81.57** | **+80.38** | **85.95%** | **MATCH** |

### 5.2 Denominator & Pairing Unit Clarification
- **Pairing Unit:** Station-year pairs $(s, y)$ where station $s$ has a valid daily observation (`is_day_valid = TRUE`, $\ge 16$ valid hourly readings) on both the immediate pre-Diwali baseline ($t-1$) and the post-Diwali night ($t+1$).
- **Denominator:** The total count of $306$ is the sum of matched station instances across all 7 festival years ($16 + 40 + 46 + 53 + 55 + 46 + 50 = 306$). It is **not** unique monitoring stations (the physical network comprises 56 CAAQMS stations).
- **Proportion Elevated:** Across all 306 station-year pairs, exactly 263 exhibited higher AQI at $t+1$ than at $t-1$:
  $$\frac{263}{306} \times 100\% = 85.95\%$$
- **Single-Station Case:** When filtered to an individual monitoring station (e.g. *Anand Vihar*), the denominator represents the number of festival years (up to 7) for which that specific station was operational and valid on both $t-1$ and $t+1$. The dashboard UI card explicitly labels this metric as **"Matched Station-Year Pairs"** and **"Station-Years Elevated"**.

### 5.3 Audit Reconciliation: Preliminary Draft (281 Pairs) vs Live Authoritative (306 Pairs)
- **Root Cause of Preliminary Figures (+65.71 AQI, 281 Pairs, 84.82% Elevated):** An earlier draft report recorded metrics from a preliminary run where stations with partial hourly missingness had been dropped from the matching pool (yielding 30 pairs in 2018, 44 in 2021, and 46 in 2023; total $281$). That 281-pair subset yielded a mean surge of $+65.71$ AQI points and $84.82\%$ elevated.
- **Empirical Ground Truth (+81.57 AQI, 306 Pairs, 85.95% Elevated):** The authoritative processed dataset (`fact_daily_aqi.parquet` and PostgreSQL `fact_daily_aqi`) adheres to CPCB statutory validation ($\ge 16$ valid hours/day). Applying this statutory criterion across all 7 years preserves 40 pairs in 2018, 55 in 2021, and 50 in 2023, totaling **306 station-year pairs**. The live Streamlit engine computes these metrics dynamically without hardcoding.

### 5.4 Timing Cohort Analysis: October Diwali vs November Diwali

| Timing Cohort | Festival Years Included | Matched Station-Years | Pooled Pre Median | Pooled Post Median | Pooled Mean Surge | Pooled Median Surge | Pooled % Elevated | Unweighted Annual Avg % Elevated |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **October Diwali** | 2017, 2019, 2022 (3 years) | **108** | 293.44 | 362.50 | **+58.92** | **+59.23** | **84.26%** (91/108) | **86.32%** |
| **November Diwali** | 2018, 2020, 2021, 2023 (4 years) | **198** | 314.36 | 392.02 | **+93.92** | **+92.54** | **86.87%** (172/198) | **87.21%** |
| **Combined / Network** | All 7 Years | **306** | 303.64 | 392.11 | **+81.57** | **+80.38** | **85.95%** (263/306) | **86.83%** |

- **Methodological Distinction (Pooled vs Unweighted):**
  - **Pooled % Elevated:** Calculated across all station-year pairs in the cohort ($\frac{\sum \text{Elevated Station-Years}}{\sum \text{Matched Station-Years}}$). This is the mathematically rigorous measure of network-wide station risk.
  - **Unweighted Annual Average %:** Simple arithmetic mean of annual percentages ($\frac{1}{K} \sum \text{pct}_y$). It treats each year equally regardless of network size (e.g. 2017 with 16 stations carries equal weight to 2021 with 55 stations).
- **October Diwali Dynamics (3 Years, 108 Pairs):** Baseline median is **293.44** (moderate pre-inversion). Generates a pooled mean surge of **+58.92 pts** (pooled median **+59.23 pts**), with **84.26%** of station-years elevating (unweighted annual average: **86.32%**).
- **November Diwali Dynamics (4 Years, 198 Pairs):** Baseline median is **314.36** (coinciding with peak crop residue burning). Generates a pooled mean surge of **+93.92 pts** (pooled median **+92.54 pts**), with **86.87%** of station-years elevating (unweighted annual average: **87.21%**).

### 5.5 Causal Deconfounding Disclaimer:
1. **Regional Agricultural Stubble Burning:** Post-monsoon paddy stubble burning in Punjab and Haryana peaks annually between October 25 and November 15, directly overlapping the Diwali calendar window.
2. **Planetary Boundary Layer Height (PBLH) Collapse:** As ambient temperatures plunge in late autumn, atmospheric mixing depth drops from $>1,500\text{m}$ to $<300\text{m}$, trapping ground-level emissions.
3. **Sensor Ceiling Saturation:** When baseline pollution approaches or exceeds 400 AQI, sensor capping at statutory 500.0 compresses the observable relative surge. Naive attribution of 100% of the post-Diwali surge to fireworks alone is scientifically invalid.

---

## 6. Defensive Programming & Quality Checks

1. **Empty Filter Handling:** Tested `filter_data()` with null/empty frames and out-of-range dates; confirmed graceful return of NaN/0 values without unhandled exceptions.
2. **Missing Station Imputation:** Zero imputation is applied to station-matched Diwali comparisons; stations missing on either $t-1$ or $t+1$ are explicitly dropped from the paired difference rather than filled with artificial zeroes.
3. **Sensor Ceiling Transparency:** Every dashboard view explicitly surfaces the statutory 500.0 ceiling count and proportion, preventing misleading claims of physical sensor precision at extreme concentrations.

---

## 7. Sign-Off & Verification

- **Automated Test Results:** `52 passed in 8.24s` (`tests/test_dashboard.py`, `tests/test_cleaning.py`, `tests/test_database.py`, `tests/test_robustness_audit.py`, `tests/test_statistics.py`).
- **PostgreSQL Database Integrity:** Verified against `delhi_aqi` on `localhost:5432`.
- **Dashboard Runtime:** Verified live at `http://localhost:8501` (HTTP 200 OK).

*Certified by Antigravity Agentic Data Analyst Engine.*
