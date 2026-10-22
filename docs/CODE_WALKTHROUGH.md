# Codebase Architecture & Code Walkthrough

This document breaks down the software design, module functions, data flow, and error-handling patterns implemented across the project.

---

## 1. Directory Structure and Architectural Purpose

```
delhi-ncr-aqi-analysis/
├── data/
│   ├── raw/                # Immutable original downloads (Parquet/CSV) - kept out of git
│   ├── processed/          # Cleaned analytical Parquet/CSV tables
│   └── sample/             # Stratified mini-dataset (676 rows) tracked in git for tests
├── notebooks/              # Interactive exploratory analysis notebooks
├── src/                    # Modular, testable Python production code
│   ├── ingestion/          # Data download, integrity checking, sample creation
│   ├── cleaning/           # Wide-to-long reshaping, typing, outlier/capping flags
│   ├── analysis/           # EDA, seasonal aggregations, diurnal pattern generators
│   ├── statistics/         # Hypothesis tests, Cliff's delta, bootstrap CIs, event studies
│   └── database/           # PostgreSQL connection, schema migration, fast batch loading
├── sql/                    # DDL schemas, indexing strategies, analytical SQL queries
├── tests/                  # Automated pytest test suites (data validation, transforms)
├── reports/
│   ├── figures/            # Production visual charts (PNG/SVG) with source attribution
│   ├── tables/             # Summary tables (CSV/Markdown)
│   └── findings/           # Pre-computed key metrics for dashboard and reports
├── dashboard/              # Power BI documentation, DAX scripts, Streamlit app
└── docs/                   # Beginner learning guides, SQL walkthrough, viva prep
```

---

## 2. Ingestion Module (`src/ingestion/download_data.py`)

### 2.1 Purpose & Role
Automates fetching the raw 14.87 MB CPCB Parquet archive from the upstream repository, verifies columnar schema integrity, and creates a lightweight sample dataset.

### 2.2 Key Functions & Implementation Highlights
- **`download_file(url, dest_path, force=False)`**:
  - Implements an HTTP download hook with a progress indicator.
  - Safe-write pattern: if a download is interrupted, incomplete files are cleanly removed to prevent silent corruption.
  - Skips re-downloading if the file already exists locally.
- **`verify_aqi_parquet(file_path)`**:
  - Uses `pyarrow.parquet.ParquetFile` to inspect low-level parquet metadata without loading millions of cells into memory.
  - Confirms the presence of core fields (`Station ID`, `State`, `City`, `Station Name`, `Date`) and row count (~562,878).
- **`create_sample_dataset(raw_parquet_path, sample_output_path)`**:
  - Filters strictly for Delhi-NCR cities (`Delhi`, `Faridabad`, `Gurugram`, `Ghaziabad`, `Noida`).
  - Implements **stratified random sampling** by `(City, Station Name, Year)`, picking 2 representative dates per station-year.
  - Produces a 676-row, 79.1 KB CSV that allows developers and reviewers to run the entire pipeline instantly without waiting for network downloads.

---

## 3. Cleaning Module (`src/cleaning/clean_data.py`) [Stage 2 Roadmap]

### 3.1 Design Specifications
- **Input**: `data/raw/cpcb-aqi.parquet`
- **Transformations**:
  1. **Filtering**: Subset rows where `City` is in Delhi-NCR (reduces memory usage by 80%).
  2. **Station Key Harmonization**: Fix the upstream `site_115` duplication by generating unique slugified station keys from `Station Name`:
     ```python
     station_key = (
         df["Station Name"]
         .str.lower()
         .str.replace(r"[^\w\s]", "", regex=True)
         .str.replace(r"\s+", "_", regex=True)
     )
     ```
  3. **Reshaping (Wide to Long)**: Use `pandas.melt()` to convert the 24 hourly columns (`00:00:00` to `23:00:00`) into a normalized long format:
     ```python
     df_long = df.melt(
         id_vars=["station_key", "State", "City", "Station Name", "Date"],
         value_vars=hour_cols,
         var_name="Hour_Str",
         value_name="AQI"
     )
     ```
  4. **Timestamp Reconstruction**: Combine `Date` and `Hour_Str` into a single Indian Standard Time (`datetime64[ns]`) timestamp.
  5. **Anomaly and Capping Flags**:
     - Flag values $> 500$ as `is_anomalous = True` (only 10 occurrences in 2.44M readings; sensor communication noise).
     - Flag values $== 500$ as `is_sensor_capped = True` (53,656 occurrences; genuine upper-bound saturation).
     - Preserve zero handling: verify whether any true 0 values exist (inspection confirmed minimum valid reading is 1.0).
- **Outputs**:
  - `data/processed/fact_hourly_aqi.parquet`: Tidy hourly observations.
  - `data/processed/fact_daily_aqi.parquet`: Station-day aggregations with 16-hour validity gate.
  - `data/processed/dim_station.csv`: Station dimension table.

---

## 4. Common Pitfalls & How We Prevent Them

| Pitfall | Beginner Mistake | Our Engineering Solution |
| :--- | :--- | :--- |
| **Silent Memory Exhaustion** | Loading nationwide hourly wide data in full Pandas objects repeatedly. | Filter to Delhi-NCR before unpivoting; use memory-efficient data types (`int8`, `float32`, `category`). |
| **Timezone Confusion** | Mixing UTC timestamps with local Diwali night celebrations (8 PM – 2 AM IST). | All timestamps standardized explicitly to `Asia/Kolkata` (IST, UTC+05:30). |
| **Deleting Extremes** | Dropping all AQI = 500 rows as "outliers". | AQI = 500 represents genuine hazardous smog; we flag it with `is_sensor_capped` and retain it in non-parametric analyses. |
| **Overwriting Raw Data** | Transforming columns in-place and saving back to `data/raw/`. | `data/raw/` is treated as strictly read-only. Cleaned outputs write to `data/processed/`. |
