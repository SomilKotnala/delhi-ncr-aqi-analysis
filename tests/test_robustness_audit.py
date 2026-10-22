"""
Automated Test Suite for Statistical Robustness & Econometric Audit Pipeline
Project: Delhi-NCR Air Quality Analysis
Author: Data Analyst Candidate
License: Open Data Commons Open Database License (ODbL 1.0)

Covers:
- Temporal and spatial autocorrelation diagnostics
- Calendar-day network aggregation and Moving Block Bootstrap (MBB)
- Balanced panel sensitivity (21 anchor stations active all 7 years)
- Year-by-year temporal invariance (2017 to 2023)
- Statutory censoring audit and Tobit latent shift estimation
- Station-matched paired Diwali event decomposition with pre-trend background drift
- Existence and non-emptiness of all audit deliverables and figures
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.statistics.robustness_audit import (
    compute_autocorrelation_diagnostics,
    run_balanced_panel_robustness,
    run_calendar_day_block_bootstrap,
    run_censoring_audit_and_tobit,
    run_diwali_causal_audit,
    run_year_by_year_invariance,
    verify_paired_station_calculations,
    verify_primary_calculations,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FINDINGS_DIR = REPORTS_DIR / "findings"
FIGURES_DIR = REPORTS_DIR / "figures"


@pytest.fixture(scope="module")
def processed_daily_df() -> pd.DataFrame:
    """Fixture to load processed daily dataset."""
    daily_path = PROCESSED_DATA_DIR / "fact_daily_aqi.parquet"
    assert daily_path.exists(), f"Daily Parquet file not found at {daily_path}"
    return pd.read_parquet(daily_path)


@pytest.fixture(scope="module")
def processed_hourly_df() -> pd.DataFrame:
    """Fixture to load processed hourly dataset (optimized memory footprint)."""
    hourly_path = PROCESSED_DATA_DIR / "fact_hourly_aqi.parquet"
    assert hourly_path.exists(), f"Hourly Parquet file not found at {hourly_path}"
    return pd.read_parquet(
        hourly_path,
        columns=["year", "diwali_relative_day", "aqi_cleaned", "is_sensor_capped", "is_winter"],
    )


def test_calculation_verification_and_paired_reconciliation(processed_daily_df: pd.DataFrame) -> None:
    """Verify independent recomputation of primary metrics and paired station reconciliation."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()

    calc_res = verify_primary_calculations(df_valid)
    assert calc_res["n_winter"] == 26753
    assert calc_res["n_non_winter"] == 74041
    assert calc_res["winter_median"] == 335.61
    assert calc_res["non_winter_median"] == 154.00
    assert calc_res["asymptotic_z_score"] > 180.0  # Massive z-score explains p=0.0 underflow
    assert calc_res["cliffs_delta"] == 0.7637

    paired_audit = verify_paired_station_calculations(df_valid, n_bootstraps=200, seed=42)
    assert paired_audit["n_stations"] == 56
    assert paired_audit["winter_station_median_center"] > 330.0  # Reconciled correct winter median
    assert paired_audit["non_winter_station_median_center"] < 160.0
    assert paired_audit["true_bootstrap_ci_95_lower"] > 170.0
    assert paired_audit["true_bootstrap_ci_95_upper"] < 195.0
    assert paired_audit["percentage_stations_elevated"] == 100.0


def test_autocorrelation_diagnostics(processed_daily_df: pd.DataFrame) -> None:
    """Verify empirical autocorrelation and contemporaneous correlation metrics."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    diag = compute_autocorrelation_diagnostics(df_valid)

    # Significant serial persistence
    assert diag["within_station_ar1_median"] > 0.80
    assert diag["regional_daily_median_ar1"] > 0.85
    assert diag["regional_daily_median_ar7"] > 0.65

    # High spatial cross-sectional correlation
    assert diag["cross_station_contemporaneous_corr_median"] > 0.85


def test_calendar_day_mbb_robustness(processed_daily_df: pd.DataFrame) -> None:
    """Verify Calendar-Day aggregation with Moving Block Bootstrap."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    res = run_calendar_day_block_bootstrap(df_valid, block_length=14, n_bootstraps=200, seed=42)

    assert res["total_calendar_days"] > 2500
    assert res["winter_calendar_median"] > 330.0
    assert res["non_winter_calendar_median"] < 165.0
    assert res["observed_ratio"] > 2.0
    assert res["cliffs_delta"] > 0.75
    assert res["mbb_ci_95_lower"] > 140.0  # Block bootstrap CI strictly > 0
    assert "Reject H0" in res["decision"]


def test_balanced_panel_robustness(processed_daily_df: pd.DataFrame) -> None:
    """Verify balanced anchor stations panel (21 stations active all 7 years)."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    res = run_balanced_panel_robustness(df_valid)

    assert res["anchor_stations_count"] == 21
    assert res["total_station_days"] > 40000
    assert res["winter_median"] > 320.0
    assert res["non_winter_median"] < 160.0
    assert res["ratio"] > 2.0
    assert res["cliffs_delta"] > 0.70


def test_year_by_year_invariance(processed_daily_df: pd.DataFrame) -> None:
    """Verify that winter elevation is statistically significant in every single year."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    years = run_year_by_year_invariance(df_valid)

    assert len(years) == 7
    for y_res in years:
        assert y_res["significant_at_01"] is True
        assert y_res["cliffs_delta"] > 0.60
        assert y_res["ratio"] >= 1.70


def test_statutory_censoring_and_tobit(
    processed_daily_df: pd.DataFrame, processed_hourly_df: pd.DataFrame
) -> None:
    """Verify statutory sensor capping audit and Tobit model latent shift."""
    res = run_censoring_audit_and_tobit(processed_daily_df, processed_hourly_df)

    assert res["hourly_winter_capped_percentage"] > 5.0
    assert res["hourly_non_winter_capped_percentage"] < 1.0
    assert res["capping_relative_risk"] > 5.0
    assert res["tobit_latent_uncensored_shift"] >= res["ols_observed_mean_shift"]
    assert res["sub_ceiling_cliffs_delta"] > 0.70


def test_diwali_station_matched_causal_audit(processed_daily_df: pd.DataFrame) -> None:
    """Verify station-matched paired Diwali analysis and pre-trend decomposition."""
    yearly_res, summary = run_diwali_causal_audit(processed_daily_df)

    assert len(yearly_res) == 7
    # Late October surges should on average be higher than mid-November surges
    assert summary["late_october_years_mean_surge"] > summary["mid_november_years_mean_surge"]

    for yr in yearly_res:
        assert yr["matched_stations_count"] > 10


def test_robustness_deliverables_exist() -> None:
    """Verify all robustness audit deliverables exist and are non-empty."""
    expected_files = [
        TABLES_DIR / "statistical_robustness_results.csv",
        TABLES_DIR / "robustness_audit_summary.json",
        FINDINGS_DIR / "statistical_robustness_audit.md",
        FIGURES_DIR / "q9_statistical_robustness_audit.png",
    ]
    for f in expected_files:
        assert f.exists(), f"File {f} does not exist"
        assert f.stat().st_size > 0, f"File {f} is empty"

    with open(TABLES_DIR / "robustness_audit_summary.json", "r", encoding="utf-8") as jf:
        data = json.load(jf)
    assert "calculation_verification" in data
    assert "calendar_day_mbb_robustness" in data
    assert "statutory_censoring_audit" in data
    assert "diwali_audit_summary" in data
