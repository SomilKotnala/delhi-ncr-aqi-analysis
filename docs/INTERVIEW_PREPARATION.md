# Interview Preparation & Viva Defense Guide

This guide prepares you to present, explain, and defend this project in Data Analyst job interviews, technical screens, and university viva presentations.

---

## 1. The 60-Second Elevator Pitch

> *"For my portfolio project, I analyzed 7 years of ambient air quality data across Delhi-NCR (2017–2023) sourced from continuous CAAQMS stations under the Open Database License. Rather than running superficial models on dirty data, I built an end-to-end reproducible analytical pipeline in Python and PostgreSQL.*
> 
> *I addressed critical real-world data challenges: resolving station-identifier duplication across 56 stations, handling right-censoring where sensors saturated at the 500 AQI ceiling (over 53,000 observations), and avoiding pseudoreplication in statistical testing by aggregating to station-day units rather than treating 2.44 million autocorrelated hourly readings as independent.*
> 
> *I designed a Kimball Star Schema in PostgreSQL with window functions and CTEs, conducted a pre-registered non-parametric hypothesis test proving winter elevation with Cliff's delta effect sizes, and built an interactive Power BI dashboard featuring Diwali event-study tracking."*

---

## 2. Technical Interview Questions & High-Scoring Answers

### Question 1: "Why did you use Parquet instead of CSV for raw storage?"
- **Candidate Answer**: 
  *"The nationwide raw dataset contains 562,878 station-day records and 29 columns. In uncompressed CSV, it consumes several hundred megabytes. Parquet utilizes columnar compression with dictionary encoding and Snappy, reducing file size to under 15 megabytes. More importantly, Parquet embeds schema metadata, preserving explicit timestamps and nullable 64-bit integers (`Int64`) without schema-inference overhead or memory spikes during ingestion."*

---

### Question 2: "What data quality issues did you uncover during inspection?"
- **Candidate Answer**: 
  *"I identified three major issues:
  1. **Upstream Key Duplication**: All 39 stations in Delhi shared the exact same `Station ID` (`site_115`) because the upstream archive mapped folder names rather than station codes. I resolved this by generating unique surrogate slug keys from `Station Name`.
  2. **Sensor Ceiling Saturation**: Exactly 53,656 hourly readings hit the CPCB formula ceiling of 500. Naive mean calculations would underestimate true peaks due to right-censoring, so I implemented non-parametric median metrics and explicit boolean capping flags.
  3. **Extreme Anomalies**: Exactly 10 observations exceeded 500 (up to 3,797), which represent electronic communication faults rather than valid NAQI scores. I isolated and flagged them rather than silently dropping rows."*

---

### Question 3: "Why couldn't you run a standard two-sample Student's t-test to compare Winter vs. Non-Winter?"
- **Candidate Answer**: 
  *"A standard t-test assumes normality, homoscedasticity, and crucially, statistical independence of observations. Air pollution data violates all three. Most critically, hourly readings exhibit strong serial autocorrelation ($\text{AR}(1) > 0.85$). If you run a t-test across 2.44 million hourly rows, the inflated degrees of freedom produce an artificially tiny standard error and a meaningless $p \approx 0$ due to pseudoreplication.
  
  To solve this, I pre-registered the hypothesis, aggregated measurements to the station-day level ($\ge 16$ valid hours per day), and used the non-parametric Mann-Whitney $U$ test and Wilcoxon signed-rank test with Cliff's delta effect size and bootstrap confidence intervals."*

---

### Question 4: "Can you walk me through your Star Schema design in PostgreSQL?"
- **Candidate Answer**: 
  *"I designed a classic Star Schema with two fact tables and two dimension tables:
  - `dim_station`: Contains station attributes, coordinates, operating agency (DPCC/CPCB/IMD), and active date ranges.
  - `dim_date`: Pre-computed calendar dimension containing year, month, season tags, winter flags, and Diwali event-study indicators.
  - `fact_hourly_aqi`: Granular fact table storing 2.44 million cleaned hourly readings, categories, and anomaly flags.
  - `fact_daily_aqi`: Aggregated station-day fact table containing mean, median, min, max, and completeness counts.
  
  Separating daily and hourly facts prevents analytical queries from repeatedly scanning 2.4 million rows when answering daily or monthly trend questions."*

---

### Question 5: "How does your Power BI dashboard handle filter context when comparing Diwali across years?"
- **Candidate Answer**: 
  *"Because Diwali shifts on the Gregorian calendar each year (e.g., October 19 in 2017 vs. November 14 in 2020), a standard calendar month filter cannot compare Diwali performance across years.
  
  I built a relative event-day index $[t-7, t+7]$ where $t_0$ represents Diwali Day for each specific year. Using DAX `CALCULATE()` with `FILTER(ALL(dim_date))`, the visual aligns all 7 festivals onto a single standardized relative-day axis, allowing executives to directly compare the magnitude of the festival pulse and post-festival dissipation."*

---

## 3. Resume Bullet Points to Use

Copy and customize these bullet points for your resume:

- *Engineered an end-to-end air quality analytics pipeline analyzing 2.44M+ hourly CAAQMS observations across 56 Delhi-NCR stations (2017–2023) using Python, PostgreSQL, and Power BI.*
- *Implemented automated data validation and cleaning routines in Pandas, addressing upstream key collisions, 53K+ upper-bound sensor saturations, and missingness thresholds.*
- *Designed a PostgreSQL Star Schema (Kimball model) utilizing CTEs, window functions (`DENSE_RANK`, rolling frames), and percentile aggregates to benchmark multi-year trends.*
- *Pre-registered and executed non-parametric hypothesis testing (Mann-Whitney U, Cliff's delta, bootstrap CIs), eliminating pseudoreplication from autocorrelated time-series data.*
- *Developed an interactive Power BI dashboard featuring dynamic DAX measures, normalized relative-time event studies for Diwali episodes, and multi-station comparative KPIs.*
