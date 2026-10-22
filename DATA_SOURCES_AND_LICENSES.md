# Data Sources, Attribution, and Licensing

## 1. Overview and Provenance

This project analyzes ambient air quality and Air Quality Index (AQI) dynamics across the National Capital Region (Delhi-NCR), India. 

All underlying monitoring data originates from continuous ambient air quality monitoring stations (CAAQMS) operated by the **Central Pollution Control Board (CPCB)**, **Delhi Pollution Control Committee (DPCC)**, **Haryana State Pollution Control Board (HSPCB)**, **Uttar Pradesh Pollution Control Board (UPPCB)**, and the **India Meteorological Department (IMD)** under the Ministry of Environment, Forest and Climate Change (MoEFCC), Government of India.

The curated historical dataset is retrieved from the open-source repository maintained by **Vonter** ([india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi)), which programmatically archives published data from the official CPCB portal endpoints.

---

## 2. Source Repositories and Portals

| Resource | Link | Role in Project |
| :--- | :--- | :--- |
| **Upstream Data Repository** | [github.com/Vonter/india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi) | Primary source for multi-year station-level Parquet and CSV files |
| **CPCB National AQI Portal** | [airquality.cpcb.gov.in/AQI_India](https://airquality.cpcb.gov.in/AQI_India/) | Official reference portal for real-time and daily AQI bulletins |
| **CPCB CAAQM Data Repository** | [airquality.cpcb.gov.in/ccr/](https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-data-repository) | Source backend for 15-minute CAAQM raw pollutant measurements |

---

## 3. Dataset Licensing Terms

### 3.1 Upstream Database License: ODbL 1.0
The curated database is made available under the **Open Data Commons Open Database License v1.0 (ODbL 1.0)**:
- Full text: [opendatacommons.org/licenses/odbl/1.0/](https://opendatacommons.org/licenses/odbl/1.0/)

Under the ODbL, users are free:
- **To Share**: To copy, distribute, and use the database.
- **To Create**: To produce works from the database.
- **To Adapt**: To modify, transform, and build upon the database.

As long as the following conditions are respected:
1. **Attribution**: Any public use of the database or derivative works must attribute the source repository (`Vonter/india-cpcb-aqi`) and the original data authority (Central Pollution Control Board).
2. **Share-Alike**: If any adapted version of this database is publicly distributed, that adapted database must also be offered under the ODbL 1.0.
3. **Keep Open**: If the database or adapted database is redistributed, no technological measures (such as DRM) restricting open access may be applied.

### 3.2 Individual Content Rights
Individual measurements and regulatory standards are published by the Central Pollution Control Board (CPCB), Government of India, for public interest, environmental awareness, and research.

---

## 4. Dataset Inspection, Scope, and Verified Metrics

The dataset was directly inspected on local disk using `pyarrow` and `pandas`. Below are the empirically verified characteristics:

| Attribute | Verified Value | Analytical Significance |
| :--- | :--- | :--- |
| **File Name** | `cpcb-aqi.parquet` | Compressed columnar format (~14.87 MB) |
| **Total Nationwide Rows** | 562,878 station-days | Entire CAAQMS network across India |
| **Delhi-NCR Subset Rows** | 111,014 station-days | Focus of this portfolio analysis |
| **Coverage Period** | **2017-01-01 to 2023-12-31** | **7 full calendar years** (2,556 consecutive days) |
| **Temporal Granularity** | Hourly measurements | 24 hourly readings per station-day (`00:00:00` to `23:00:00`) |
| **Delhi-NCR Total Station-Hours** | 2,664,336 possible observations | $111,014 \times 24$ |
| **Valid Recorded Station-Hours** | 2,441,802 observations | **91.65% valid coverage** across 7 years |
| **Missing Station-Hours** | 222,534 observations | **8.35% missing data rate** |
| **Monitored NCR Cities** | **5 cities** | Delhi, Faridabad, Gurugram, Ghaziabad, Noida |
| **Total Monitored NCR Stations** | **56 unique stations** | Verified by distinct station names across the 5 cities |

### Station Breakdown by City
- **Delhi**: 39 stations (e.g., Anand Vihar, IGI Airport, Punjabi Bagh, Mandir Marg, R K Puram, Jahangirpuri)
- **Faridabad (Haryana)**: 4 stations (Sector 11, Sector 30, Sector-16A, New Industrial Town)
- **Gurugram (Haryana)**: 4 stations (Vikas Sadan, NISE Gwal Pahari, Sector-51, Teri Gram)
- **Ghaziabad (Uttar Pradesh)**: 3 stations (Indirapuram, Loni, Vasundhara)
- **Noida / Greater Noida (Uttar Pradesh)**: 6 stations (Sector 62, Sector 125, Sector-1, Sector-116, Knowledge Park III, Knowledge Park V)

---

## 5. Data Ingestion & Reproducibility Protocol

To ensure reproducible analysis and comply with GitHub file-size best practices:
1. **Raw Data Isolation**: Large raw binary files (`.parquet`, `.csv.gz`) are strictly kept inside `data/raw/` and excluded from version control via `.gitignore`.
2. **Automated Fetch Script**: Anyone cloning this repository can reproduce the entire ingestion step with:
   ```bash
   python src/ingestion/download_data.py
   ```
3. **Committed Sample Slice**: A stratified 676-row sample (`data/sample/delhi_ncr_aqi_sample.csv`) covering all 56 stations and all 7 years is tracked in Git, allowing immediate execution of unit tests, schema verifications, and pipeline validation without downloading the multi-megabyte raw archive.
