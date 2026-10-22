"""
Automated Pytest Suite for Data Cleaning and Reshaping Pipeline
===============================================================
Tests:
  - Reshaping logic (wide-to-long 24-hour expansion)
  - Station surrogate key generation and preservation of raw ID
  - Normalized timestamp derivation (IST & UTC conversion)
  - Sensor capping (=500) and telemetry anomaly (>500) handling
  - Official CPCB AQI categorization
  - Season and Diwali window assignment
  - Integration on committed sample dataset
  - Schema integrity and non-emptiness of generated processed datasets
"""

import sys
import json
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

# Add project root to python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.cleaning.clean_data import (
    slugify,
    generate_station_key,
    extract_agency,
    assign_season,
    assign_aqi_category,
    clean_and_reshape_aqi,
    NCR_CITIES,
    DIWALI_DATES,
)


# ============================================================================
# 1. Unit Tests for Helper Functions
# ============================================================================

def test_slugify():
    assert slugify("Anand Vihar Delhi DPCC") == "anand_vihar_delhi_dpcc"
    assert slugify("Sector- 16A Faridabad HSPCB") == "sector_16a_faridabad_hspcb"
    assert slugify("IGI Airport (T3) Delhi IMD") == "igi_airport_t3_delhi_imd"


def test_station_key_uniqueness():
    k1 = generate_station_key("Delhi", "Anand Vihar Delhi DPCC")
    k2 = generate_station_key("Delhi", "Mandir Marg Delhi DPCC")
    assert k1 != k2
    assert k1.startswith("delhi_")


def test_extract_agency():
    assert extract_agency("Anand Vihar Delhi DPCC") == "DPCC"
    assert extract_agency("DTU Delhi CPCB") == "CPCB"
    assert extract_agency("IGI Airport (T3) Delhi IMD") == "IMD"
    assert extract_agency("Sector 11 Faridabad HSPCB") == "HSPCB"
    assert extract_agency("Sector 62 Noida UPPCB") == "UPPCB"
    assert extract_agency("Chandni Chowk Delhi IITM") == "IITM"
    assert extract_agency("Unknown Station") == "OTHER"


def test_assign_season():
    assert assign_season(11) == "Winter"
    assert assign_season(12) == "Winter"
    assert assign_season(1) == "Winter"
    assert assign_season(4) == "Summer / Pre-Monsoon"
    assert assign_season(7) == "Monsoon"
    assert assign_season(10) == "Post-Monsoon"
    assert assign_season(2) == "Transition (Feb)"


def test_assign_aqi_category():
    assert assign_aqi_category(25) == "Good"
    assert assign_aqi_category(50) == "Good"
    assert assign_aqi_category(51) == "Satisfactory"
    assert assign_aqi_category(100) == "Satisfactory"
    assert assign_aqi_category(101) == "Moderate"
    assert assign_aqi_category(200) == "Moderate"
    assert assign_aqi_category(201) == "Poor"
    assert assign_aqi_category(300) == "Poor"
    assert assign_aqi_category(301) == "Very Poor"
    assert assign_aqi_category(400) == "Very Poor"
    assert assign_aqi_category(401) == "Severe"
    assert assign_aqi_category(500) == "Severe"
    assert assign_aqi_category(501) == "Anomalous"
    assert pd.isna(assign_aqi_category(np.nan))


# ============================================================================
# 2. Reshaping, Timestamps, and Anomaly Handling on Synthetic Data
# ============================================================================

@pytest.fixture
def sample_wide_df():
    """Constructs a minimal wide dataframe mimicking CPCB raw format."""
    hours = [f"{h:02d}:00:00" for h in range(24)]
    data = {
        "Station ID": ["site_115", "site_115", "site_5341"],
        "State": ["Delhi", "Delhi", "Haryana"],
        "City": ["Delhi", "Delhi", "Faridabad"],
        "Station Name": ["Anand Vihar Delhi DPCC", "Mandir Marg Delhi DPCC", "Sector 11 Faridabad HSPCB"],
        "Date": [pd.Timestamp("2017-10-19"), pd.Timestamp("2017-10-20"), pd.Timestamp("2017-10-19")]
    }
    for h in hours:
        data[h] = [150, 500, np.nan]
    # Inject an anomaly > 500 in hour 11
    data["11:00:00"] = [3303, 500, np.nan]
    return pd.DataFrame(data)


def test_reshaping_multiplies_by_24(sample_wide_df):
    fact_hourly, fact_daily, dim_station, metrics = clean_and_reshape_aqi(sample_wide_df)
    assert len(fact_hourly) == len(sample_wide_df) * 24
    assert len(fact_daily) == len(sample_wide_df)
    assert len(dim_station) == 3


def test_timestamp_normalization(sample_wide_df):
    fact_hourly, _, _, _ = clean_and_reshape_aqi(sample_wide_df)
    first_row = fact_hourly.iloc[0]
    
    # Check IST timestamp
    expected_ist = first_row["date"] + pd.Timedelta(hours=first_row["hour"])
    assert first_row["timestamp_ist"] == expected_ist
    
    # Check UTC is exactly 5 hours 30 mins behind IST
    expected_utc = expected_ist - pd.Timedelta(hours=5, minutes=30)
    assert first_row["timestamp_utc"] == expected_utc
    
    # Check hour is 0-23
    assert set(fact_hourly["hour"].unique()) == set(range(24))


def test_sensor_ceiling_and_anomaly_flags(sample_wide_df):
    fact_hourly, _, _, metrics = clean_and_reshape_aqi(sample_wide_df)
    
    # Test capping at 500
    capped_rows = fact_hourly[fact_hourly["aqi_raw"] == 500.0]
    assert len(capped_rows) > 0
    assert capped_rows["is_sensor_capped"].all()
    assert capped_rows["is_valid"].all()
    assert (capped_rows["aqi_category"] == "Severe").all()

    # Test anomaly > 500 (value 3303 injected at 11:00:00)
    anom_rows = fact_hourly[fact_hourly["aqi_raw"] == 3303.0]
    assert len(anom_rows) == 1
    assert anom_rows["is_anomalous"].iloc[0] == True
    assert anom_rows["is_valid"].iloc[0] == False
    assert pd.isna(anom_rows["aqi_cleaned"].iloc[0])

    # Test missing values
    missing_rows = fact_hourly[fact_hourly["is_missing"]]
    assert len(missing_rows) > 0
    assert missing_rows["is_valid"].apply(lambda v: not v).all()


def test_diwali_event_window_assignment(sample_wide_df):
    fact_hourly, _, _, _ = clean_and_reshape_aqi(sample_wide_df)
    
    # 2017-10-19 is verified Diwali day for 2017
    diwali_day_rows = fact_hourly[fact_hourly["date"] == pd.Timestamp("2017-10-19")]
    assert diwali_day_rows["is_diwali_window"].all()
    assert (diwali_day_rows["diwali_relative_day"] == 0.0).all()

    # 2017-10-20 is Diwali + 1 day
    diwali_plus_1 = fact_hourly[fact_hourly["date"] == pd.Timestamp("2017-10-20")]
    assert diwali_plus_1["is_diwali_window"].all()
    assert (diwali_plus_1["diwali_relative_day"] == 1.0).all()


# ============================================================================
# 3. Integration Test on Committed Sample Dataset
# ============================================================================

def test_pipeline_on_committed_sample():
    sample_file = PROJECT_ROOT / "data" / "sample" / "delhi_ncr_aqi_sample.csv"
    assert sample_file.exists(), f"Sample file missing at {sample_file}"
    
    sample_df = pd.read_csv(sample_file)
    n_sample_rows = len(sample_df)
    assert n_sample_rows > 0
    
    fact_hourly, fact_daily, dim_station, metrics = clean_and_reshape_aqi(sample_df)
    
    # Row count expansion check
    assert len(fact_hourly) == n_sample_rows * 24
    assert len(fact_daily) == n_sample_rows
    
    # Station surrogate key check
    assert fact_hourly["station_key"].nunique() == dim_station["station_key"].nunique()
    assert dim_station["station_key"].nunique() <= 56
    
    # Completeness check
    assert metrics["valid_hourly_records"] + metrics["missing_hourly_records"] + metrics["anomalous_records"] == len(fact_hourly)


# ============================================================================
# 4. Verification Tests on Generated Processed Datasets (Full Execution)
# ============================================================================

def test_processed_files_exist_and_match_manifest():
    hourly_p = PROJECT_ROOT / "data" / "processed" / "fact_hourly_aqi.parquet"
    daily_p = PROJECT_ROOT / "data" / "processed" / "fact_daily_aqi.parquet"
    station_p = PROJECT_ROOT / "data" / "processed" / "dim_station.csv"
    metrics_p = PROJECT_ROOT / "reports" / "tables" / "data_quality_metrics.json"
    report_p = PROJECT_ROOT / "reports" / "DATA_QUALITY_REPORT.md"
    
    assert hourly_p.exists() and hourly_p.stat().st_size > 0
    assert daily_p.exists() and daily_p.stat().st_size > 0
    assert station_p.exists() and station_p.stat().st_size > 0
    assert metrics_p.exists() and metrics_p.stat().st_size > 0
    assert report_p.exists() and report_p.stat().st_size > 0


def test_processed_dataset_row_counts_and_keys():
    hourly_p = PROJECT_ROOT / "data" / "processed" / "fact_hourly_aqi.parquet"
    daily_p = PROJECT_ROOT / "data" / "processed" / "fact_daily_aqi.parquet"
    station_p = PROJECT_ROOT / "data" / "processed" / "dim_station.csv"
    
    # Read metadata or fast sample
    dim_st = pd.read_csv(station_p)
    assert len(dim_st) == 56, f"Expected 56 stations, found {len(dim_st)}"
    assert dim_st["station_key"].nunique() == 56
    
    daily_df = pd.read_parquet(daily_p)
    assert len(daily_df) == 111014, f"Expected 111,014 daily records, found {len(daily_df)}"
    assert daily_df["station_key"].nunique() == 56
    
    # Check that daily valid rows have valid completeness
    valid_daily = daily_df[daily_df["is_day_valid"]]
    assert (valid_daily["valid_hours_count"] >= 16).all()
    
    # Check metrics json
    metrics_p = PROJECT_ROOT / "reports" / "tables" / "data_quality_metrics.json"
    with open(metrics_p, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    assert metrics["total_hourly_records"] == 2664336
    assert metrics["unique_stations"] == 56
    assert metrics["sensor_capped_records"] == 53656
    assert metrics["anomalous_records"] == 10
