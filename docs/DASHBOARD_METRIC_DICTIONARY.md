# Dashboard Metric Dictionary: Delhi-NCR Air Quality Analysis

**Document Version:** 1.0.0  
**Project Root:** `D:\delhi-ncr-aqi-analysis`  
**Applicability:** Universal reference for Power BI Desktop DAX measures, SQL queries, and Streamlit application metrics.

This metric dictionary provides unambiguous definitions, mathematical formulas, grain specifications, denominators, and plain-English interpretations for all KPIs and visual calculations across the reporting suite.

---

## 1. Metric Hierarchy & Granularity Rules

| Grain Level | Table Source | Unit of Observation | Description & Usage |
| :--- | :--- | :--- | :--- |
| **Station-Hour** | `fact_hourly_aqi` | 1 station at 1 hourly timestamp | Used for diurnal profiling, statutory sensor capping frequency ($AQI = 500$), and official AQI category percentage distributions. |
| **Station-Day** | `fact_daily_aqi` | 1 station on 1 calendar date | **Primary analytical grain**. Used for network KPIs, spatial comparisons, station rankings, and winter/non-winter seasonal tests. |
| **Calendar-Day** | `dim_date` aggregated | 1 calendar date across the airshed | Used for econometric robustness audits (zero station pseudoreplication) and regional time-series trendlines. |
| **Station** | `dim_station` | 1 physical monitoring station | Metadata, geographic jurisdiction, operating agency, and 7-year uptime completeness. |

> **Guiding Principle**: Never combine or average metrics across incompatible grains without explicit weighting. A daily mean must not be averaged with an hourly reading.

---

## 2. Core Operational Metrics & KPIs

### Metric 1: Valid Station-Days
- **Metric Name**: `Valid Station-Days` (`[Total Valid Station Days]`)
- **Business Question**: How many station-days meet the regulatory data-completeness threshold to be analytically reliable?
- **Data Grain**: Station-Day (`fact_daily_aqi`)
- **Completeness Threshold**: A day is valid (`is_day_valid = TRUE`) if and only if it contains $\ge 16$ valid hourly readings out of 24 (CPCB / NAQI standard requirement).
- **Formula**:
  $$\text{Valid Station-Days} = \sum_{i=1}^{N} \mathbb{I}(\text{valid\_hours\_count}_i \ge 16)$$
- **DAX Implementation**:
  ```dax
  Total Valid Station Days = 
  CALCULATE(
      COUNTROWS(fact_daily_aqi),
      fact_daily_aqi[is_day_valid] = TRUE()
  )
  ```
- **SQL Implementation**:
  ```sql
  SELECT COUNT(*) FROM fact_daily_aqi WHERE is_day_valid = TRUE;
  ```
- **Numerator**: Count of station-days where `valid_hours_count >= 16`.
- **Denominator**: Total recorded station-days (111,014 across 2017–2023).
- **Unit**: Count (Integer).
- **Missing Data Treatment**: Station-days with $< 16$ valid hours have `is_day_valid = FALSE`. They are tracked for completeness audits but excluded from pollution aggregation.
- **Plain-English Interpretation**: The count of full days of air monitoring that had enough operating hours (at least 16 out of 24) to be trusted for statistical analysis.

---

### Metric 2: Median Daily Mean AQI
- **Metric Name**: `Median Daily Mean AQI` (`[Median Daily AQI]`)
- **Business Question**: What is the typical ambient air quality level across monitoring stations in the selected scope?
- **Data Grain**: Station-Day (`fact_daily_aqi`)
- **Formula**:
  $$\text{Median Daily AQI} = \text{Median}\left(\{ \text{daily\_mean\_aqi}_i \mid \text{is\_day\_valid}_i = \text{TRUE} \}\right)$$
- **DAX Implementation**:
  ```dax
  Median Daily AQI = 
  CALCULATE(
      MEDIAN(fact_daily_aqi[daily_mean_aqi]),
      fact_daily_aqi[is_day_valid] = TRUE()
  )
  ```
- **SQL Implementation**:
  ```sql
  SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY daily_mean_aqi)
  FROM fact_daily_aqi
  WHERE is_day_valid = TRUE;
  ```
- **Numerator / Denominator**: Non-parametric 50th percentile rank ordering of station-day averages.
- **Unit**: AQI Index Points ($0 - 500$ scale).
- **Missing Data Treatment**: Excluded if `is_day_valid = FALSE`.
- **Plain-English Interpretation**: The middle value of daily air quality averages. We use the median rather than the mean because air pollution data is heavily skewed by extreme winter smog spikes and right-censored at 500.

---

### Metric 3: Severe-Band Hourly Proportion
- **Metric Name**: `Severe-Band Hourly Proportion` (`[% Severe Hours]`)
- **Business Question**: What percentage of monitored time is air quality in the hazardous "Severe" category ($\text{AQI} > 400$)?
- **Data Grain**: Station-Hour (`fact_hourly_aqi`)
- **Formula**:
  $$\% \text{ Severe Hours} = \frac{\sum \mathbb{I}(\text{aqi\_cleaned} > 400)}{\sum \mathbb{I}(\text{aqi\_cleaned is not null})} \times 100$$
- **DAX Implementation**:
  ```dax
  % Severe Hours = 
  DIVIDE(
      CALCULATE(COUNTROWS(fact_hourly_aqi), fact_hourly_aqi[aqi_cleaned] > 400),
      CALCULATE(COUNTROWS(fact_hourly_aqi), NOT(ISBLANK(fact_hourly_aqi[aqi_cleaned]))),
      0
  )
  ```
- **Numerator**: Valid hourly observations with $\text{AQI} \in (400, 500]$.
- **Denominator**: Total valid hourly observations ($2,441,792$ across 7 years).
- **Unit**: Percentage ($0.0\% - 100.0\%$).
- **Missing Data Treatment**: Missing telemetry hours ($222,534$ hours, $8.35\%$) and anomalies ($10$ hours) are excluded from both numerator and denominator.
- **Plain-English Interpretation**: The percentage of all monitored hours where breathing the air is considered dangerous to healthy individuals and severe for vulnerable groups according to CPCB health standards.

---

### Metric 4: Winter Elevation Ratio & Shift
- **Metric Name**: `Winter Elevation Ratio` (`[Winter Elevation Ratio]`) and `Winter AQI Shift` (`[Winter AQI Shift]`)
- **Business Question**: How much more severe is air pollution during the stagnant winter period compared to the rest of the year?
- **Data Grain**: Station-Day (`fact_daily_aqi`)
- **Pre-Registered Operational Definitions**:
  - **Winter Period ($\text{Period}_W$)**: November 1 to January 31 ($92$ calendar days/year; captures temperature inversions and calm winds).
  - **Non-Winter Baseline ($\text{Period}_{NW}$)**: February 1 to October 31 ($273/274$ calendar days/year).
- **Formulas**:
  $$\text{Winter Shift} = \text{Median}_W - \text{Median}_{NW}$$
  $$\text{Winter Elevation Ratio} = \frac{\text{Median}_W}{\text{Median}_{NW}}$$
- **DAX Implementation**:
  ```dax
  Winter Median AQI = 
  CALCULATE(
      [Median Daily AQI],
      dim_date[is_winter] = TRUE()
  )

  Non-Winter Median AQI = 
  CALCULATE(
      [Median Daily AQI],
      dim_date[is_winter] = FALSE()
  )

  Winter AQI Shift = [Winter Median AQI] - [Non-Winter Median AQI]

  Winter Elevation Ratio = 
  DIVIDE([Winter Median AQI], [Non-Winter Median AQI], 0)
  ```
- **Verified Benchmark**:
  - Winter Median: **335.61** ($n = 26,753$ station-days)
  - Non-Winter Median: **154.00** ($n = 74,041$ station-days)
  - Shift: **+181.61 points**
  - Ratio: **2.18x** (Winter air is more than twice as polluted as the non-winter baseline).
- **Plain-English Interpretation**: Compares the median pollution level during the cold, stagnant winter months (Nov–Jan) to the warmer, ventilated months (Feb–Oct).

---

### Metric 5: Monitoring Network Coverage
- **Metric Name**: `Active Monitoring Stations` (`[Active Stations]`) and `Network Uptime %` (`[Network Completeness %]`)
- **Business Question**: How many physical monitoring stations are reporting, and what is the temporal completeness of the network?
- **Data Grain**: Station Dimension (`dim_station`) and Fact Daily (`fact_daily_aqi`)
- **Formulas**:
  $$\text{Active Stations} = \text{DISTINCTCOUNT}(\text{fact\_daily\_aqi}[\text{station\_key}])$$
  $$\text{Network Completeness \%} = \frac{\text{Total Valid Station-Days}}{\text{Total Possible Station-Days}} \times 100$$
- **DAX Implementation**:
  ```dax
  Active Stations = DISTINCTCOUNT(fact_daily_aqi[station_key])

  Network Completeness % = 
  DIVIDE(
      [Total Valid Station Days],
      COUNTROWS(fact_daily_aqi),
      0
  )
  ```
- **Plain-English Interpretation**: The count of unique monitoring stations operating in the selected city or timeframe, and the percentage of scheduled station-days that yielded valid data.

---

### Metric 6: Official CPCB AQI Severity Category Distribution
- **Metric Name**: `CPCB Category Distribution %`
- **Business Question**: How are hourly air quality observations distributed across the statutory health impact tiers?
- **Data Grain**: Station-Hour (`fact_hourly_aqi`)
- **Official CPCB Category Brackets**:
  1. **Good**: $0 - 50$ (Hex: `#009639`) — Minimal impact.
  2. **Satisfactory**: $51 - 100$ (Hex: `#7ec242`) — Minor breathing discomfort to sensitive people.
  3. **Moderate**: $101 - 200$ (Hex: `#fdd023`) — Breathing discomfort to people with lungs, asthma, and heart diseases.
  4. **Poor**: $201 - 300$ (Hex: `#f58220`) — Breathing discomfort to most people on prolonged exposure.
  5. **Very Poor**: $301 - 400$ (Hex: `#e62b1e`) — Respiratory illness on prolonged exposure.
  6. **Severe**: $401 - 500$ (Hex: `#9b111e`) — Affects healthy people and seriously impacts those with existing diseases.
- **Formula**:
  $$\% \text{ in Category } c = \frac{\sum \mathbb{I}(\text{aqi\_category} = c)}{\sum \mathbb{I}(\text{aqi\_cleaned is not null})} \times 100$$
- **Plain-English Interpretation**: The percentage breakdown of all valid hourly air readings into the 6 official government health alert bands.

---

### Metric 7: Statutory Sensor Ceiling Capping Rate
- **Metric Name**: `Sensor Capping Prevalence %` (`[% Capped Hours]`)
- **Business Question**: What proportion of hourly readings hit the statutory NAQI ceiling of 500.0?
- **Data Grain**: Station-Hour (`fact_hourly_aqi`)
- **Formula**:
  $$\% \text{ Capped Hours} = \frac{\sum \mathbb{I}(\text{aqi\_raw} = 500.0)}{\sum \mathbb{I}(\text{aqi\_cleaned is not null})} \times 100$$
- **DAX Implementation**:
  ```dax
  % Capped Hours = 
  DIVIDE(
      CALCULATE(COUNTROWS(fact_hourly_aqi), fact_hourly_aqi[is_sensor_capped] = TRUE()),
      CALCULATE(COUNTROWS(fact_hourly_aqi), NOT(ISBLANK(fact_hourly_aqi[aqi_cleaned]))),
      0
  )
  ```
- **Plain-English Interpretation**: The percentage of hours where air pollution reached or exceeded the maximum measurable limit of the official index (500). When air hits 500, true pollution is often higher, but the index formula stops calculating.

---

### Metric 8: Diwali Event Episode Metrics
- **Metric Names**: `Pre-Event Baseline`, `Event Peak AQI`, `Station-Matched Paired Surge`, `Pre-Trend Drift`
- **Business Question**: How does ambient air quality change during the Diwali festival window relative to pre-event baselines and seasonal background trends?
- **Event Windows**:
  - **Pre-Event Baseline**: $t-7$ to $t-1$ relative to verified festival date.
  - **Event Window**: $t_0$ to $t+1$ (festival day and immediate following morning).
  - **Post-Event Window**: $t+2$ to $t+7$.
  - **Pre-Trend Window**: $t-14$ to $t-8$ (used to measure background seasonal ramp).
- **Formulas**:
  $$\text{Pre-Event Median} = \text{Median}(\text{AQI}_{t \in [-7, -1]})$$
  $$\text{Event Median} = \text{Median}(\text{AQI}_{t \in [0, 1]})$$
  $$\text{Station-Matched Paired Surge } (\Delta_s) = \text{Median}_{s \in \text{Event}} - \text{Median}_{s \in \text{Pre}}$$
  $$\text{Pre-Trend Background Drift} = \text{Median}_{s \in [-7, -1]} - \text{Median}_{s \in [-14, -8]}$$
  $$\text{Net Excess Festival Shock} = \Delta_s - \text{Pre-Trend Drift}$$
- **Plain-English Interpretation**: 
  - *Station-Matched Surge*: The median increase experienced by individual monitoring stations during Diwali compared to their own reading in the preceding week.
  - *Pre-Trend Drift*: The natural upward climb in regional pollution that was already occurring due to autumn weather cooling and regional crop residue burning.
- **Causal Disclaimer**: A surge in air pollution around Diwali reflects joint episodic festival emissions, seasonal upwind agricultural residue burning, and concurrent meteorological boundary layer collapse. It must NOT be attributed solely to fireworks without meteorological controls.
