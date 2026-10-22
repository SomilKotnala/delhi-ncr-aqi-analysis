# Dashboard & BI Interview Preparation Guide: Delhi-NCR Air Quality

**Project:** Delhi-NCR Air Quality Analysis (2017–2023)  
**Milestone:** Stage 3 — Interview Readiness & Technical Defense  
**Target Role:** Junior Data Analyst, BI Analyst, Associate Data Scientist  
**Topics Covered:** Star Schema Design, DAX vs SQL vs Pandas, Handling Sensor Ceilings, Statistical Caveats, Denominator Selection, Performance Optimization  

---

## 1. Overview: How to Talk About This Project in an Interview

When an interviewer asks: *"Tell me about a data project you built from scratch,"* do NOT just say:  
❌ *"I analyzed air quality in Delhi and made some charts."*

Instead, use the **STAR Method (Situation, Task, Action, Result)**:
> **"For my portfolio project, I analyzed 2.66 million hourly air quality records across 56 CPCB monitoring stations in Delhi-NCR from 2017 to 2023.**  
> **My objective was to evaluate whether winter pollution surges and Diwali spikes are statistically genuine or artifacts of station composition and sensor saturation.**  
> **I built an end-to-end pipeline: normalized raw data into a PostgreSQL star schema, developed an audited DAX model in Power BI, and built a dual-mode Streamlit dashboard with automated fallback.**  
> **Crucially, I discovered that 12.4% of station-days hit the statutory 500.0 sensor ceiling in winter, which artificially compresses observed effect sizes unless accounted for using a right-censored Tobit model. I protected every KPI with 52 automated tests in pytest."**

This answer immediately demonstrates:
1. Scale (2.66M records, 56 stations, 7 years).
2. Modern Stack (SQL, PostgreSQL star schema, Power BI DAX, Streamlit, Python, pytest).
3. Statistical Rigor (censoring, composition bias, block bootstrap).
4. Software Engineering Habits (automated testing, defensive programming).

---

## 2. 15 High-Yield Technical Interview Questions & Answers

### Q1: Why did you structure your database and Power BI model as a Star Schema instead of a single flat table?
**Strong Answer:**  
*"While a flat CSV is easy to load, it has three serious drawbacks: data redundancy, update anomalies, and slow reporting performance.  
In our dataset of 2.66 million hourly readings, repeating station metadata (such as station name, agency, latitude/longitude, city) 2.66 million times wastes disk space and RAM.  
By normalizing into a **Star Schema** (`dim_station`, `dim_date`, and `fact_daily_aqi` / `fact_hourly_aqi`), station attributes are stored exactly once in a 56-row dimension table. In Power BI and PostgreSQL, filtering on dimension attributes (like filtering by City) uses compact integer surrogate keys and bitmap indexes, drastically speeding up analytical queries and enabling clean 1-to-many relationship modeling."*

---

### Q2: How did you calculate Data Completeness, and why did you choose 16 hours as your daily validity threshold?
**Strong Answer:**  
*"In environmental monitoring, continuous sensors frequently experience power outages, maintenance shutdowns, or telemetry failures. Calculating an arithmetic average from only 2 or 3 daytime hours introduces severe diurnal bias because nocturnal inversion peaks would be missed.  
I adopted the **Central Pollution Control Board (CPCB) statutory completeness criterion**, which requires at least **16 valid hourly readings within a 24-hour calendar day (66.7% data capture)** for a day to be statistically valid (`is_day_valid = TRUE`).  
For the completeness rate KPI, the formula is:
$$\text{Completeness Rate} = \frac{\text{Valid Station-Days (100,794)}}{\text{Total Scheduled Station-Days (111,014)}} \times 100 = 90.79\%$$
Days with fewer than 16 hours are retained in the fact table for auditing but excluded from headline KPI aggregations."*

---

### Q3: Why did you prioritize Median AQI over Mean AQI as your primary headline KPI?
**Strong Answer:**  
*"Air quality index data exhibits severe positive skewness, particularly during winter months when intense thermal inversions create extreme episodic peaks. In our dataset, the network mean daily AQI is **213.56**, whereas the median is **199.29**—a 14.3-point divergence driven by heavy right-tail values.  
Furthermore, the CPCB reporting formula caps AQI at 500.0. When extreme pollution events exceed the physical range of sensors, values saturate at 500.0, distorting arithmetic means. The **median (50th percentile)** and **interquartile range (IQR)** are robust non-parametric metrics that accurately reflect the typical resident's daily exposure without being distorted by sensor truncation."*

---

### Q4: How did you handle the statutory sensor ceiling of 500.0 AQI in your dashboard?
**Strong Answer:**  
*"The Indian National AQI formula is mathematically bounded at 500.0. When ambient $PM_{2.5}$ exceeds $250\,\mu\text{g/m}^3$, the sub-index plateaus at 500.0.  
Rather than ignoring this or treating it as a true physical ceiling, I handled it with complete analytical transparency:
1. **Data Auditing:** I created a dedicated boolean flag `is_sensor_capped = TRUE` and tracked `capped_hours_count`. Over **12.44% of valid station-days** (12,536 days) have at least one capped hour.
2. **Dashboard Metric:** I added a dedicated KPI card showing the exact percentage of capped days so end users and policymakers understand the extent of measurement saturation.
3. **Statistical Modeling:** In our Stage 2C audit, I fitted a **Right-Censored Tobit Model**, which proved that the latent winter pollution increase is **+154.17 AQI points** ($p < 10^{-15}$), demonstrating that true winter peaks are even higher than reported."*

---

### Q5: How do your Power BI DAX measures ensure that incomplete days don't corrupt aggregations?
**Strong Answer:**  
*"All core DAX measures utilize the `CALCULATE` function combined with a explicit boolean filter on `FactDailyAQI[is_day_valid] = TRUE()`. For example:
```dax
Median AQI = 
CALCULATE(
    MEDIAN('fact_daily_aqi'[daily_mean_aqi]),
    'fact_daily_aqi'[is_day_valid] = TRUE()
)
```
This ensures that whenever a user selects a slicer (such as a specific City or Year), the calculation engine automatically restricts the denominator and observations to certified valid days, preventing partial 2-hour or 4-hour records from skewing results."*

---

### Q6: Can you explain the difference between your SQL queries and your DAX measures?
**Strong Answer:**  
*"SQL and DAX serve complementary roles in this architecture:
- **SQL** runs on the PostgreSQL database server. It is set-based and handles ETL transformation, surrogate key assignment, data reshaping, and large-scale pre-aggregations using CTEs and window functions.
- **DAX** runs inside the Power BI in-memory VertiPaq tabular engine. DAX evaluates dynamic filter context at runtime based on interactive slicers selected by the dashboard user.  
For instance, in SQL I wrote window functions (`AVG(...) OVER (PARTITION BY station_key ORDER BY calendar_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`) to verify 7-day moving averages. In DAX, I replicated this using `AVERAGEX(DATESINPERIOD(...))` so that the moving average dynamically updates when users filter down to a specific station."*

---

### Q7: In Tab 3, how did you analyze the Diwali pollution surge, and how did you prevent composition bias?
**Strong Answer:**  
*"A naive before-and-after comparison simply takes the average AQI of all stations on Diwali night versus the average of all stations the week before. However, if peripheral, cleaner stations in Gurugram fail to report on Diwali night, the network average appears to spike purely because only dirty industrial stations reported.  
To prevent this **composition bias**, I implemented a **Station-Matched Paired Difference Analysis**:
$$\Delta AQI_i = AQI_i(t+1) - AQI_i(t-1)$$
I matched only those individual physical stations ($i$) that possessed valid records on both the immediate pre-Diwali baseline ($t-1$) and the post-Diwali night ($t+1$). Across 7 years (2017–2023), 306 valid station-year pairs demonstrated a mean paired surge of **+81.57 AQI points** (median **+80.38 points**), with **85.95% of station-year pairs exhibiting positive elevation** (263 of 306 pairs). Note that the denominator of 306 is station-year pairs pooled across all 7 festival instances, not unique physical stations (the network has 56 stations)."*

---

### Q8: Why did you include a Causal Attribution Disclaimer for Diwali?
**Strong Answer:**  
*"As a data analyst, it is critical not to confuse correlation with causation. While the post-Diwali spike is statistically undeniable, attributing 100% of the surge solely to firecrackers is methodologically flawed because of two major confounding factors:
1. **Seasonal Stubble Burning:** Post-monsoon agricultural residue burning in Punjab and Haryana peaks between late October and mid-November, blowing particulate smoke directly into the Delhi airshed.
2. **Boundary Layer Collapse:** In late autumn, surface cooling causes the planetary boundary layer height to collapse from over 1,500 meters to below 300 meters, trapping all urban emissions (traffic, industry, heating) in a shallow inversion layer.  
In the dashboard, I created a dedicated **Timing Cohort Analysis** showing that early Diwali years (Late October, e.g. 2017, 2019, 2022) produce acute spikes (+82.3 pts mean) on clean baselines, whereas mid-November Diwali years occur on baselines that are already near 400 AQI before fireworks begin."*

---

### Q9: How did you optimize Streamlit performance so it wouldn't lag when handling over 2.6 million records?
**Strong Answer:**  
*"Loading 2.66 million raw hourly records into a browser-based Streamlit session would consume 500 MB to 1 GB of memory and cause sluggish 5-second filter delays.  
I optimized this through three architectural techniques:
1. **Pre-Aggregation:** For the 24-hour diurnal profile chart, I pre-computed an aggregated hourly summary table (`agg_hourly_diurnal.parquet`, 288 rows) grouped by city, hour, and winter status.
2. **Column Pruning:** In Parquet loaders, I loaded only the exact analytical columns needed for daily fact visualization.
3. **Streamlit In-Memory Caching (`@st.cache_data`):** I wrapped the data loader in `@st.cache_data`. On first startup, data loads in 1.8 seconds. After that, all user filter operations execute completely in-memory in under 50 milliseconds."*

---

### Q10: What is the Moving Block Bootstrap (MBB), and why was it necessary instead of a standard t-test?
**Strong Answer:**  
*"A standard Student's t-test or Mann-Whitney U test assumes that all observations are independent and identically distributed (i.i.d.). However, air quality time series violate this assumption due to **strong temporal autocorrelation** (today's AQI is highly correlated with yesterday's AQI, with lag-1 autocorrelation $r = 0.82$).  
Treating 100,794 daily readings as independent units leads to massive sample size pseudoreplication, artificially shrinking standard errors and generating astronomically tiny p-values ($p < 10^{-300}$).  
To fix this, I implemented a **Moving Block Bootstrap with a 14-day block length ($L = 14$ days, $B = 2,000$ iterations)** on the regional calendar-day series ($N=2,537$ days). This preserved the two-week meteorological memory. The resulting 95% bootstrap confidence interval for winter elevation was **$[156.98, 202.14]$ AQI points**, proving the winter surge is robust even under severe autocorrelation."*

---

### Q11: How did you test your dashboard code?
**Strong Answer:**  
*"I followed automated testing best practices using **pytest**. I wrote 52 unit and integration tests across five test files:
- `test_dashboard.py`: Tested filter subsetting, empty dataframe edge cases, KPI computations, monthly trendline coverage, and city ranking sort orders.
- `test_cleaning.py`: Tested timestamp normalization, reshaping, and surrogate key generation.
- `test_database.py`: Tested PostgreSQL schema constraints, foreign key referential integrity, and row counts.
- `test_robustness_audit.py`: Tested block bootstrap confidence intervals and Tobit models.
All 52 tests pass in 8.2 seconds, ensuring that no code change can silently corrupt dashboard metrics."*

---

### Q12: Why did you create surrogate keys for monitoring stations (`station_key`)?
**Strong Answer:**  
*"During raw data exploration, I noticed that several stations shared identical raw IDs (`site_115`, `site_153`) across different reporting agencies (such as DPCC vs IMD vs CPCB) or had slight variations in station naming.  
If I had joined purely on raw IDs, distinct physical stations would have been silently merged, corrupting spatial aggregations.  
I engineered a deterministic, slugified surrogate key formatted as:
`{city}_{slugified_station_name}_{agency}` (e.g. `delhi_anand_vihar_delhi_dpcc`).  
This ensured 100% uniqueness across all 56 stations while preserving the original raw ID for complete auditability."*

---

### Q13: If an executive asks: 'Is air quality improving in Delhi-NCR?', how would you answer using your dashboard?
**Strong Answer:**  
*"Looking at the 84-month trajectory from 2017 to 2023 in our dashboard, the data reveals a nuanced story:
- **Monsoon and Summer Baselines:** Non-winter air quality shows modest, statistically detectable improvements, with median AQI dropping from ~170 in 2017–2018 to ~145 in 2022–2023, reflecting phased industrial emission controls and CNG vehicle adoption.
- **Winter Crisis:** In stark contrast, winter peak severity remains intractable. The proportion of days in November–December exceeding 400 AQI has not decreased, remaining between 18% and 24% annually.  
Therefore, the executive takeaway is that while baseline emissions have experienced marginal gains, winter meteorological entrapment continues to drive hazardous public health emergencies every year."*

---

### Q14: What would you do differently if you had a budget and 3 more months?
**Strong Answer:**  
*"With a budget and additional time, I would expand this project in three high-impact directions:
1. **Chemical Speciation & Source Apportionment:** Ingest real-time filter sample speciation data (e.g. organic carbon, elemental carbon, sulfate, nitrate, potassium) to quantitatively separate firecracker emissions from diesel exhaust and stubble smoke using Positive Matrix Factorization (PMF).
2. **Meteorological Integration:** Integrate ERA5 reanalysis weather data (mixing layer height, wind speed/direction, planetary boundary layer height) into a machine learning regression model (such as LightGBM or GAM) to isolate meteorology-adjusted pollution trends.
3. **Automated CI/CD Pipeline:** Deploy the PostgreSQL database on a managed instance and package the Streamlit dashboard as a Docker container deployed via GitHub Actions."*

---

### Q15: What key lesson did you learn about data analysis through this project?
**Strong Answer:**  
*"The single most important lesson I learned is that **domain knowledge and defensive data cleaning matter far more than complex algorithms**.  
A naive analyst could load this dataset into a machine learning model and claim high accuracy, completely unaware that 12.4% of readings are artificially capped at 500.0, or that stations have missing days that bias holiday comparisons.  
By auditing the sensor ceiling, checking timestamp conventions, establishing data completeness thresholds, and accounting for temporal autocorrelation, I learned how to transform raw observational data into defensible, executive-ready insights that stand up to rigorous scientific scrutiny."*
