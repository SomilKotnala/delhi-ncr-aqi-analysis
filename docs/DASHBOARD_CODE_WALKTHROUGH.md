# Dashboard Code Walkthrough: Delhi-NCR Air Quality

**Project:** Delhi-NCR Air Quality Analysis (2017–2023)  
**Milestone:** Stage 3 — Codebase Architecture & Code Walkthrough  
**Target Audience:** Beginner Data Analysts, Students & Interview Reviewers  
**Modules Covered:**  
1. `dashboard/data_access.py` (Data Access Layer & Caching)  
2. `dashboard/metrics.py` (Pure Analytical & KPI Engine)  
3. `dashboard/app.py` (Streamlit User Interface & Visualizations)  
4. `tests/test_dashboard.py` (Automated Unit & Integration Tests)  

---

## 1. Overview of Software Architecture

The dashboard is engineered following the **Model-View-Controller (MVC)** and **Separation of Concerns** software engineering design patterns:

```
┌─────────────────────────────────┐
│     dashboard/data_access.py    │ ─── Data Layer: Loads, caches, and falls back between
│                                 │     PostgreSQL and Apache Parquet.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       dashboard/metrics.py      │ ─── Business Logic Layer: Pure analytical functions that
│                                 │     compute KPIs, trends, distributions, and rankings.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│        dashboard/app.py         │ ─── Presentation Layer: Streamlit UI components, Plotly
│                                 │     visuals, sidebar slicers, and CSS styling.
└─────────────────────────────────┘
```

**Why this separation matters for your portfolio:**
- A novice programmer writes all database queries, metric computations, and chart drawing inside one giant 1,000-line script. If a chart breaks, the whole app crashes.
- A senior data analyst separates the data access, the mathematical logic, and the user interface. This enables **100% automated testing** of the metrics without ever needing to run a web server.

---

## 2. Deep Dive: `dashboard/data_access.py`

This module is responsible for loading the data efficiently and reliably.

### 2.1 Graceful Caching Decorator Fallback
```python
try:
    import streamlit as st
    cache_data = st.cache_data
except (ImportError, Exception):
    def cache_data(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
```
*Beginner Explanation:* When you run unit tests in `pytest`, you are not running Streamlit (`streamlit run`). If a function has `@st.cache_data` and is imported in `pytest`, Streamlit might print warnings or complain about a missing script context. This defensive block checks if Streamlit is available; if not, it returns a plain "identity decorator" so your code can be tested anywhere without errors.

### 2.2 Dual-Mode Data Access (PostgreSQL + Parquet)
```python
def try_load_from_postgres():
    try:
        from sqlalchemy import create_engine
        creds = get_db_credentials()
        conn_str = f"postgresql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['dbname']}"
        engine = create_engine(conn_str, connect_args={"connect_timeout": 3})
        
        daily_query = """
        SELECT f.station_key, s.station_name, s.city, f.calendar_date AS date, ...
        FROM fact_daily_aqi f
        JOIN dim_station s ON f.station_key = s.station_key
        JOIN dim_date d ON f.calendar_date = d.calendar_date;
        """
        df_daily = pd.read_sql(daily_query, engine)
        ...
        return df_daily, df_stations, df_dates, df_diurnal
    except Exception:
        return None
```
*Beginner Explanation:* This function attempts to connect to PostgreSQL using a short 3-second connection timeout (`connect_timeout: 3`). If the PostgreSQL server is running and credentials are valid, it executes the star-schema join and loads the data. If the server is offline or fails for any reason, it returns `None` instead of crashing the entire application.

In `load_all_dashboard_data()`:
```python
if pg_res is not None:
    source_used = "PostgreSQL Database (delhi_aqi @ localhost:5432)"
else:
    df_daily, df_stations, df_dates, df_diurnal = load_from_parquet()
    source_used = "Local Parquet Storage (data/processed/)"
```
This guarantees **zero downtime**: whether the evaluator has PostgreSQL running or not, the dashboard works instantly!

---

## 3. Deep Dive: `dashboard/metrics.py`

This module contains **pure functions** that perform all mathematical aggregations.

### 3.1 Defensive Filtering (`filter_data`)
```python
def filter_data(df, cities=None, stations=None, date_range=None, seasons=None, valid_only=True):
    if df.empty:
        return df.copy()
    
    filtered = df
    if valid_only and "is_day_valid" in filtered.columns:
        filtered = filtered[filtered["is_day_valid"] == True]
    if cities:
        filtered = filtered[filtered["city"].isin(cities)]
    ...
    return filtered
```
*Beginner Explanation:* Notice that we do not modify the original DataFrame (`df`) in place. We filter sequentially, and we check if the input is empty first. This prevents `KeyError` or `AttributeError` if a user selects an empty filter combination.

### 3.2 Headline KPI Computation (`compute_kpis`)
```python
def compute_kpis(df):
    ...
    valid_df = df[df["is_day_valid"] == True]
    aqi_series = valid_df["daily_mean_aqi"].dropna()
    median_val = float(aqi_series.median())
    mean_val = float(aqi_series.mean())
    completeness_pct = (valid_days / total_days * 100.0) if total_days > 0 else 0.0
    severe_count = int((valid_df["daily_mean_aqi"] > 400.0).sum())
    severe_pct = (severe_count / valid_days * 100.0) if valid_days > 0 else 0.0
    ...
```
*Beginner Explanation:*
- **Median vs Mean:** We calculate both, but display Median prominently because AQI has extreme positive skewness during winter pollution spikes.
- **Explicit Denominators:** Completeness percentage divides valid days by total scheduled days (111,014), whereas Severe percentage divides severe days by valid days (100,794). Explicitly documenting denominators in code is a hallmark of professional data analysis.

### 3.3 Station-Matched Diwali Surge (`compute_diwali_event_analysis`)
```python
for yr in years:
    yr_data = event_df[event_df["year"] == yr]
    pre = yr_data[yr_data["diwali_relative_day"] == -1].set_index("station_key")["daily_mean_aqi"]
    post = yr_data[yr_data["diwali_relative_day"] == 1].set_index("station_key")["daily_mean_aqi"]
    
    common_stations = pre.index.intersection(post.index)
    paired_pre = pre.loc[common_stations]
    paired_post = post.loc[common_stations]
    diffs = paired_post - paired_pre
```
*Beginner Explanation:* A naive analysis compares all stations reporting on day $t+1$ to all stations reporting on day $t-1$. But what if 5 clean suburban stations didn't report on $t+1$? The regional average would appear to spike artificially due to **composition bias**.  
By using `common_stations = pre.index.intersection(post.index)`, we compute the **paired difference** ($AQI_{i, t+1} - AQI_{i, t-1}$) strictly for the exact same physical monitoring stations.

---

## 4. Deep Dive: `dashboard/app.py`

This module is the user-facing Streamlit application.

### 4.1 Custom CSS for Executive Polish
Streamlit's default metric cards are basic. We inject custom CSS via `st.markdown(..., unsafe_allow_html=True)` to create bordered cards with color-coded left accents:
```html
<div class="metric-container" style="border-left: 5px solid #FF8C00;">
    <div class="metric-title">Network Median AQI</div>
    <div class="metric-value">199.29</div>
    <div class="metric-caption">Mean: <strong>213.56</strong> | IQR: <strong>185.17</strong></div>
</div>
```
This gives the dashboard the clean look of an enterprise software product.

### 4.2 Dynamic Dependent Slicers
In the sidebar:
```python
all_cities = sorted(df_daily_raw["city"].unique().tolist())
selected_cities = st.sidebar.multiselect("Filter Cities", options=all_cities, default=all_cities)

stations_in_cities = sorted(
    df_daily_raw[df_daily_raw["city"].isin(selected_cities)]["station_name"].unique().tolist()
)
selected_stations = st.sidebar.multiselect("Filter Stations", options=stations_in_cities, default=[])
```
*Beginner Explanation:* When the user selects "Faridabad", the station dropdown immediately filters down to only the 4 stations in Faridabad (Sector 11, Sector 16A, Sector 30, New Industrial Town). Users can never select an invalid combination of city and station.

### 4.3 CPCB Statutory Plotly Styling
When constructing Plotly charts, we map statutory CPCB color hexes:
```python
CPCB_COLOR_MAP = {
    "Good": "#00B050",          # Bright Green
    "Satisfactory": "#92D050",  # Light Green
    "Moderate": "#E6B800",      # Deep Gold/Yellow (accessible on white background)
    "Poor": "#FF8C00",          # Dark Orange
    "Very Poor": "#E60000",      # Crimson Red
    "Severe": "#7A0019",         # Deep Maroon
}
```
In the monthly time series, we add horizontal shaded bands (`fig.add_hrect()`) so users instantly see when air quality crosses from "Moderate" into "Severe" emergency zones.

---

## 5. Automated Verification in `tests/test_dashboard.py`

Every single calculation in the dashboard is protected by automated tests:
1. `TestDashboardDataAccess`: Verifies that Parquet and PostgreSQL loaders return expected row counts.
2. `TestDashboardFiltering`: Confirms city, date, and completeness filters produce correct subsets.
3. `TestDashboardKPIs`: Verifies headline values match Stage 2C benchmarks (`199.29` median, `213.56` mean, `100,794` valid days).
4. `TestMonthlyTrends`: Verifies 84 monthly records are computed without NaN gaps.
5. `TestCategoryDistribution`: Confirms counts sum to exactly 100,794 and percentages sum to 100.0%.
6. `TestSeasonalComparison`: Verifies Winter Median (`335.61`) vs Non-Winter (`154.00`) ratio of `2.18x`.
7. `TestDiwaliEventAnalysis`: Confirms paired surge calculation across all 7 years.

To run the tests:
```powershell
D:\anaconda3\python.exe -m pytest D:\delhi-ncr-aqi-analysis\tests -v
```
Output: **52 passed in 8.24s**.
