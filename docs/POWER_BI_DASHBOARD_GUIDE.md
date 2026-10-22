# Power BI Desktop Dashboard Guide: Delhi-NCR Air Quality

This guide provides complete, beginner-friendly instructions to construct the professional, multi-page **Delhi-NCR Air Quality Dashboard** in **Power BI Desktop** using the prepared data files and pre-written DAX measures.

---

## 1. Prerequisites and Source Data Files

Power BI Desktop is already installed on your system (`Microsoft Power BI Desktop`).

The data model uses the three clean tables located in `data/processed/` (or directly from PostgreSQL):
1. **`dim_station.csv`**: Station dimension (56 stations, City, State, Agency, Coverage).
2. **`dim_date.csv`**: Calendar dimension (2017–2023, Season, Winter Flag, Diwali Relative Day).
3. **`fact_daily_aqi.csv`**: Aggregated daily measurements (Mean, Median, Min, Max, Severity Category).
4. **`fact_hourly_aqi.csv`** (Optional for detailed drill-through).

---

## 2. Step-by-Step Data Model Setup

### Step 2.1 Import Data
1. Launch **Power BI Desktop**.
2. Click **Get Data** > **Text/CSV**.
3. Navigate to `D:\delhi-ncr-aqi-analysis\data\processed\` and load:
   - `dim_station.csv`
   - `dim_date.csv`
   - `fact_daily_aqi.csv`
4. Click **Load**.

### Step 2.2 Configure Star Schema Relationships
In the **Model View** (left pane icon with three connected boxes):
- Drag `dim_station[station_key]` $\to$ `fact_daily_aqi[station_key]` (Relationship: **1 to Many**, Cross-filter: **Single**).
- Drag `dim_date[calendar_date]` $\to$ `fact_daily_aqi[calendar_date]` (Relationship: **1 to Many**, Cross-filter: **Single**).

```
   [dim_station] (1) ────< (*) [fact_daily_aqi] (*) >──── (1) [dim_date]
```

---

## 3. Core DAX Measures Specification

Create a dedicated measure table: **Home** > **Enter Data** > Name it `_DAX_Measures`. Add the following measures:

### Measure 1: Network Median AQI
```dax
Median AQI = 
MEDIAN('fact_daily_aqi'[daily_mean_aqi])
```

### Measure 2: Valid Station-Days Count
```dax
Total Monitored Station-Days = 
COUNTROWS('fact_daily_aqi')
```

### Measure 3: Severe Days Count & Percentage
```dax
Severe Days Count = 
CALCULATE(
    COUNTROWS('fact_daily_aqi'),
    'fact_daily_aqi'[daily_mean_aqi] > 400
)

Severe Day % = 
DIVIDE([Severe Days Count], [Total Monitored Station-Days], 0)
```

### Measure 4: Winter Median AQI
```dax
Winter Median AQI = 
CALCULATE(
    [Median AQI],
    'dim_date'[is_winter] = TRUE()
)
```

### Measure 5: Non-Winter Median AQI
```dax
Non-Winter Median AQI = 
CALCULATE(
    [Median AQI],
    'dim_date'[is_winter] = FALSE()
)
```

### Measure 6: Winter-to-Non-Winter Pollution Ratio
```dax
Winter Elevation Ratio = 
DIVIDE([Winter Median AQI], [Non-Winter Median AQI], 0)
```

### Measure 7: 7-Day Moving Average AQI
```dax
Rolling 7D AQI = 
AVERAGEX(
    DATESINPERIOD(
        'dim_date'[calendar_date],
        LASTDATE('dim_date'[calendar_date]),
        -7,
        DAY
    ),
    [Median AQI]
)
```

### Measure 8: Diwali Event Peak Delta
```dax
Diwali Peak Increase % = 
VAR PreEventMedian = 
    CALCULATE(
        [Median AQI],
        'dim_date'[diwali_relative_day] >= -7 && 'dim_date'[diwali_relative_day] <= -1
    )
VAR EventPeakMedian = 
    CALCULATE(
        [Median AQI],
        'dim_date'[diwali_relative_day] >= 0 && 'dim_date'[diwali_relative_day] <= 1
    )
RETURN
    DIVIDE(EventPeakMedian - PreEventMedian, PreEventMedian, 0)
```

---

## 4. Multi-Page Dashboard Design & Visual Layout

### Page 1: Executive Overview & Network KPIs
- **Header**: "Delhi-NCR Ambient Air Quality Monitor (2017–2023)" with CPCB source attribution.
- **Top Slicers**: Year (Multi-select dropdown), City (Tile selection), Station Name (Searchable dropdown).
- **Top KPI Cards**:
  1. *Overall Median AQI* (Formatted with conditional color).
  2. *Total Monitored Station-Days* (e.g., 100K+).
  3. *Severe Days Share* (e.g., % of days > 400).
  4. *Winter Elevation Ratio* (e.g., 2.1x).
- **Primary Visual (Line Chart)**: 7-Year AQI trajectory over time showing seasonal waves.
- **Secondary Visual (Stacked Bar Chart)**: AQI category distribution by year (Good, Satisfactory, Moderate, Poor, Very Poor, Severe) using standard CPCB color hexes.

### Page 2: Station & City Spatial Heterogeneity
- **Visual 1 (Clustered Bar Chart)**: Top 10 Most Polluted Stations ranked by Median Winter AQI.
- **Visual 2 (Clustered Bar Chart)**: Cleanest 10 Stations ranked by Median Annual AQI.
- **Visual 3 (Matrix / Heatmap Table)**: City vs. Year matrix showing annual median AQI.
- **Visual 4 (Scatter Plot)**: Station Coverage % (x-axis) vs. Median AQI (y-axis) to identify whether dirtier stations have more missing data.

### Page 3: Seasonal & Monthly Breakdown
- **Visual 1 (Line Chart by Month)**: 12-month annual cycle (January through December) with separate lines for each year, highlighting the massive October-November inflection.
- **Visual 2 (Donut Chart)**: Proportion of Severe Days by Season (Winter vs. Post-Monsoon vs. Monsoon vs. Pre-Monsoon).
- **Visual 3 (Box / Ribbon Chart)**: Monthly AQI spread showing Interquartile Range (IQR).

### Page 4: Diwali Pollution Episode Event Study
- **Visual 1 (Multi-Year Overlay Line Chart)**:
  - **X-Axis**: Relative Day to Diwali ($t-7$ to $t+7$).
  - **Y-Axis**: Network Median AQI.
  - **Legend**: Year (2017 to 2023).
  - Demonstrates how across all 7 years, AQI jumps sharply at $t_0$ and evaluates how quickly it returns to baseline.
- **Visual 2 (KPI Cards)**: Pre-Diwali Baseline vs. Festival Peak vs. Dissipation Time.
- **Context Card**: Transparent disclaimer regarding meteorological inversion and biomass burning co-factors.

---

## 5. Official CPCB Color Palette Palette Setting

To set custom theme colors in Power BI: **View** > **Themes** > **Customize Current Theme**:
- Good: `#009639`
- Satisfactory: `#7EC242`
- Moderate: `#FDD023`
- Poor: `#F58220`
- Very Poor: `#E62B1E`
- Severe: `#9B111E`
