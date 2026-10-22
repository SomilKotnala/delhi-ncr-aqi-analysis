"""
Automated Test Suite for Statistical Hypothesis Testing & Event Study Pipeline
Project: Delhi-NCR Air Quality Analysis
Author: Data Analyst Candidate
License: Open Data Commons Open Database License (ODbL 1.0)

Covers:
- Non-parametric effect size calculations (Cliff's Delta bounds and interpretations)
- Vectorized bootstrap confidence interval estimation
- Distribution summary statistics and shape diagnostics
- Primary pre-registered hypothesis test execution
- Paired repeated-measures station-level Wilcoxon signed-rank test
- Secondary extreme meteorological sensitivity test
- City-level subgroup analysis with Benjamini-Hochberg FDR correction
- Multi-year Diwali event-study modeling and reporting ceiling detection
- File existence and schema validation for all statistical deliverables
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.statistics.hypothesis_testing import (
    compute_bootstrap_median_diff,
    compute_cliffs_delta,
    compute_descriptive_stats,
    interpret_cliffs_delta,
    run_city_subgroup_analysis,
    run_diwali_event_study_modeling,
    run_paired_station_test,
    run_primary_hypothesis_test,
    run_sensitivity_core_winter_vs_monsoon,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FINDINGS_DIR = REPORTS_DIR / "findings"


@pytest.fixture(scope="module")
def processed_daily_df() -> pd.DataFrame:
    """Fixture to load processed daily dataset."""
    daily_path = PROCESSED_DATA_DIR / "fact_daily_aqi.parquet"
    assert daily_path.exists(), f"Daily Parquet file not found at {daily_path}"
    return pd.read_parquet(daily_path)


@pytest.fixture(scope="module")
def processed_hourly_df() -> pd.DataFrame:
    """Fixture to load processed hourly dataset."""
    hourly_path = PROCESSED_DATA_DIR / "fact_hourly_aqi.parquet"
    assert hourly_path.exists(), f"Hourly Parquet file not found at {hourly_path}"
    return pd.read_parquet(hourly_path)


def test_cliffs_delta_mathematical_bounds_and_interpretation() -> None:
    """Verify Cliff's Delta strictly satisfies -1 <= d <= 1 and classification."""
    # Complete dominance: x > y for all pairs
    x_dom = np.array([10.0, 11.0, 12.0, 13.0])
    y_dom = np.array([1.0, 2.0, 3.0, 4.0])
    d_dom, interp_dom = compute_cliffs_delta(x_dom, y_dom)
    assert d_dom == 1.0, f"Expected Cliff's delta = 1.0, got {d_dom}"
    assert interp_dom == "Large"

    # Reverse dominance: x < y for all pairs
    d_rev, interp_rev = compute_cliffs_delta(y_dom, x_dom)
    assert d_rev == -1.0, f"Expected Cliff's delta = -1.0, got {d_rev}"
    assert interp_rev == "Large"

    # Identical groups: d = 0
    x_same = np.array([5.0, 5.0, 5.0])
    y_same = np.array([5.0, 5.0, 5.0])
    d_same, interp_same = compute_cliffs_delta(x_same, y_same)
    assert d_same == 0.0, f"Expected Cliff's delta = 0.0, got {d_same}"
    assert interp_same == "Negligible"

    # Threshold checks
    assert interpret_cliffs_delta(0.10) == "Negligible"
    assert interpret_cliffs_delta(0.25) == "Small"
    assert interpret_cliffs_delta(0.40) == "Medium"
    assert interpret_cliffs_delta(0.60) == "Large"


def test_bootstrap_confidence_interval_soundness() -> None:
    """Verify bootstrap confidence interval encapsulates observed difference."""
    rng = np.random.default_rng(123)
    x = rng.normal(loc=300.0, scale=30.0, size=500)
    y = rng.normal(loc=150.0, scale=30.0, size=500)

    res = compute_bootstrap_median_diff(x, y, n_bootstraps=500, ci_level=0.95, random_state=42)

    assert res["ci_lower"] <= res["observed_median_diff"] <= res["ci_upper"]
    assert res["ci_lower"] > 100.0  # Clear physical separation
    assert res["bootstrap_se"] > 0.0


def test_descriptive_stats_structure_and_moments() -> None:
    """Verify compute_descriptive_stats returns all expected distribution moments."""
    data = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 100.0])
    stats_dict = compute_descriptive_stats(data, "test_group")

    assert stats_dict["group"] == "test_group"
    assert stats_dict["sample_size"] == 6
    assert stats_dict["min"] == 10.0
    assert stats_dict["max"] == 100.0
    assert stats_dict["median"] == 35.0
    assert stats_dict["iqr"] > 0.0
    assert stats_dict["skewness"] > 0.0  # Positive skew due to 100.0


def test_primary_hypothesis_test(processed_daily_df: pd.DataFrame) -> None:
    """Verify primary pre-registered hypothesis test (Winter vs Non-Winter)."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    assert len(df_valid) == 100794, f"Unexpected valid station days count: {len(df_valid)}"

    res = run_primary_hypothesis_test(df_valid, n_bootstraps=200, random_state=42)

    assert res["n_winter"] == 26753
    assert res["n_non_winter"] == 74041
    assert res["winter_median"] > res["non_winter_median"]
    assert res["observed_ratio"] > 2.0  # Winter is more than 2x Non-Winter
    assert res["p_value_one_tailed"] < 1e-100
    assert res["cliffs_delta"] > 0.70  # Massive effect size
    assert res["cliffs_delta_interpretation"] == "Large"
    assert res["bootstrap_median_diff_ci_lower"] > 170.0
    assert "Reject H0" in res["decision"]


def test_paired_station_wilcoxon_test(processed_daily_df: pd.DataFrame) -> None:
    """Verify paired Wilcoxon test confirms spatial invariance across all 56 stations."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    res = run_paired_station_test(df_valid)

    assert res["total_active_stations"] == 56
    assert res["stations_with_positive_elevation"] == 56
    assert res["percentage_stations_elevated"] == 100.0
    assert res["min_station_diff"] > 100.0  # Even cleanest station has >100 pts winter rise
    assert res["p_value"] < 1e-5
    assert res["rank_biserial_correlation"] == 1.0


def test_sensitivity_core_winter_vs_monsoon(processed_daily_df: pd.DataFrame) -> None:
    """Verify secondary sensitivity test (Dec-Jan vs Jul-Aug)."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    res = run_sensitivity_core_winter_vs_monsoon(df_valid, n_bootstraps=200, random_state=42)

    assert res["core_winter_median"] > 300.0
    assert res["monsoon_median"] < 100.0
    assert res["observed_ratio"] > 3.0  # Dec-Jan is ~3.5x Monsoon
    assert res["cliffs_delta"] > 0.90  # Near-complete separation
    assert res["p_value"] < 1e-100


def test_city_subgroup_fdr_significance(processed_daily_df: pd.DataFrame) -> None:
    """Verify all 5 NCR cities exhibit large, statistically significant winter elevation."""
    df_valid = processed_daily_df[processed_daily_df["is_day_valid"]].copy()
    city_results = run_city_subgroup_analysis(df_valid)

    assert len(city_results) == 5
    cities = {r["city"] for r in city_results}
    assert cities == {"Delhi", "Faridabad", "Ghaziabad", "Gurugram", "Noida"}

    for cr in city_results:
        assert cr["fdr_significant_at_01"] is True
        assert cr["cliffs_delta"] > 0.60
        assert cr["effect_size"] == "Large"
        assert cr["elevation_ratio"] >= 2.0


def test_diwali_event_study_modeling(
    processed_daily_df: pd.DataFrame, processed_hourly_df: pd.DataFrame
) -> None:
    """Verify 7-year Diwali event study dynamics and 500.0 sensor capping."""
    yearly_metrics, pooled_summary = run_diwali_event_study_modeling(
        processed_daily_df, processed_hourly_df
    )

    assert len(yearly_metrics) == 7
    years = [m["year"] for m in yearly_metrics]
    assert years == [2017, 2018, 2019, 2020, 2021, 2022, 2023]

    for ym in yearly_metrics:
        # Every year reaches the statutory 500.0 ceiling during the event window
        assert ym["peak_hourly_aqi"] == 500.0
        assert ym["capped_sensor_hours"] > 100  # Pervasive saturation
        assert ym["pre_event_n"] > 0
        assert ym["event_n"] > 0
        assert ym["post_event_n"] > 0

    # Pooled surge is positive and statistically significant
    assert pooled_summary["pooled_absolute_surge"] > 40.0
    assert pooled_summary["p_value"] < 1e-10
    assert "causal_caveat" in pooled_summary


def test_statistical_deliverable_artifacts_exist() -> None:
    """Verify all output files, tables, JSON summary, and findings report physically exist."""
    expected_files = [
        TABLES_DIR / "statistical_test_results.csv",
        TABLES_DIR / "seasonal_summary_stats.csv",
        TABLES_DIR / "city_statistical_comparison.csv",
        TABLES_DIR / "diwali_event_metrics.csv",
        TABLES_DIR / "hypothesis_testing_summary.json",
        FINDINGS_DIR / "statistical_findings.md",
        REPORTS_DIR / "figures" / "q8_statistical_hypothesis_distributions.png",
    ]

    for fpath in expected_files:
        assert fpath.exists(), f"Deliverable file {fpath} does not exist"
        assert fpath.stat().st_size > 0, f"Deliverable file {fpath} is empty"

    # Validate JSON payload structure
    summary_json_path = TABLES_DIR / "hypothesis_testing_summary.json"
    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "primary_hypothesis_test" in data
    assert "paired_station_test" in data
    assert "sensitivity_core_winter_vs_monsoon" in data
    assert "city_subgroup_analysis" in data
    assert "diwali_yearly_metrics" in data
    assert "diwali_pooled_summary" in data
