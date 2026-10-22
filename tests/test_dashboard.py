"""
tests/test_dashboard.py
=======================
Automated test suite for dashboard data access, KPI computation,
and filtering integrity.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from dashboard.data_access import load_all_dashboard_data, load_from_parquet
from dashboard.metrics import (
    CPCB_CATEGORIES,
    CPCB_COLOR_MAP,
    filter_data,
    compute_kpis,
    compute_monthly_trend,
    compute_city_summary,
    compute_category_distribution,
    compute_seasonal_comparison,
    compute_station_rankings,
    compute_diwali_event_analysis,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@pytest.fixture(scope="module")
def benchmark_daily_df():
    """Load the ground-truth processed fact daily dataset."""
    daily_file = PROCESSED_DIR / "fact_daily_aqi.parquet"
    assert daily_file.exists(), f"Benchmark data file missing: {daily_file}"
    df = pd.read_parquet(daily_file)
    df["date"] = pd.to_datetime(df["date"])
    return df


class TestDashboardDataAccess:
    """Validate data loading and fallback capabilities."""

    def test_load_from_parquet(self):
        df_daily, df_stations, df_dates, df_diurnal = load_from_parquet()
        assert not df_daily.empty
        assert len(df_daily) == 111014
        assert not df_stations.empty
        assert len(df_stations) == 56
        assert not df_dates.empty
        assert len(df_dates) == 2556
        assert not df_diurnal.empty

    def test_load_all_dashboard_data_auto(self):
        data = load_all_dashboard_data(preferred_source="auto")
        assert "daily" in data
        assert "stations" in data
        assert "dates" in data
        assert "diurnal" in data
        assert "source_info" in data
        info = data["source_info"]
        assert info["daily_rows"] == 111014
        assert info["valid_days"] == 100794
        assert info["stations_count"] == 56
        assert len(info["cities"]) == 5


class TestDashboardFiltering:
    """Validate data filtering logic under normal and edge conditions."""

    def test_filter_by_city(self, benchmark_daily_df):
        filtered = filter_data(benchmark_daily_df, cities=["Delhi"])
        assert not filtered.empty
        assert set(filtered["city"].unique()) == {"Delhi"}

    def test_filter_by_multiple_cities(self, benchmark_daily_df):
        target = ["Delhi", "Noida"]
        filtered = filter_data(benchmark_daily_df, cities=target)
        assert set(filtered["city"].unique()).issubset(set(target))

    def test_filter_by_valid_only(self, benchmark_daily_df):
        valid = filter_data(benchmark_daily_df, valid_only=True)
        assert len(valid) == 100794
        assert (valid["is_day_valid"] == True).all()

        all_records = filter_data(benchmark_daily_df, valid_only=False)
        assert len(all_records) == 111014

    def test_filter_by_date_range(self, benchmark_daily_df):
        start = pd.Timestamp("2020-01-01")
        end = pd.Timestamp("2020-12-31")
        filtered = filter_data(benchmark_daily_df, date_range=(start, end))
        assert not filtered.empty
        assert filtered["date"].min() >= start
        assert filtered["date"].max() <= end
        assert (filtered["year"] == 2020).all()

    def test_filter_empty_dataframe(self):
        empty_df = pd.DataFrame()
        res = filter_data(empty_df, cities=["Delhi"])
        assert res.empty


class TestDashboardKPIs:
    """Validate KPI calculation against audited Stage 2C benchmarks."""

    def test_full_benchmark_kpis(self, benchmark_daily_df):
        kpis = compute_kpis(benchmark_daily_df)

        # Reconcile against audited Stage 2C benchmark numbers
        assert kpis["total_station_days"] == 111014
        assert kpis["valid_station_days"] == 100794
        assert kpis["completeness_pct"] == pytest.approx(90.79, abs=0.05)

        # Median and Mean AQI
        assert kpis["median_aqi"] == pytest.approx(199.29, abs=0.2)
        assert kpis["mean_aqi"] == pytest.approx(213.56, abs=0.2)

        # Severe days (>400 AQI)
        assert kpis["severe_days_count"] == 6389
        assert kpis["severe_days_pct"] == pytest.approx(6.34, abs=0.05)

        # Capped days (hours with AQI = 500)
        assert kpis["capped_days_count"] == 12536
        assert kpis["capped_days_pct"] == pytest.approx(12.44, abs=0.05)

        # Stations
        assert kpis["active_stations_count"] == 56

    def test_empty_kpi_defensive_behavior(self):
        empty_df = pd.DataFrame()
        kpis = compute_kpis(empty_df)
        assert np.isnan(kpis["median_aqi"])
        assert kpis["valid_station_days"] == 0
        assert kpis["completeness_pct"] == 0.0


class TestMonthlyTrends:
    """Validate time-series aggregation."""

    def test_monthly_trend_shape_and_coverage(self, benchmark_daily_df):
        trend = compute_monthly_trend(benchmark_daily_df)
        assert not trend.empty
        # 7 years * 12 months = 84 months
        assert len(trend) == 84
        expected_cols = {"year_month", "year", "month", "median_aqi", "mean_aqi", "p25_aqi", "p75_aqi", "count"}
        assert expected_cols.issubset(set(trend.columns))
        # Ensure median is within plausible range
        assert (trend["median_aqi"] > 0).all()
        assert (trend["median_aqi"] < 450).all()

    def test_monthly_trend_empty(self):
        res = compute_monthly_trend(pd.DataFrame())
        assert res.empty


class TestCitySummary:
    """Validate city-level metrics and rankings."""

    def test_city_summary_metrics(self, benchmark_daily_df):
        summary = compute_city_summary(benchmark_daily_df)
        assert len(summary) == 5
        cities = set(summary["city"])
        assert cities == {"Delhi", "Faridabad", "Ghaziabad", "Gurugram", "Noida"}

        # Sorted descending by median
        medians = summary["median_aqi"].tolist()
        assert medians == sorted(medians, reverse=True)

        # Total valid days across cities equals 100,794
        assert summary["valid_station_days"].sum() == 100794


class TestCategoryDistribution:
    """Validate CPCB category distribution."""

    def test_category_distribution_totals(self, benchmark_daily_df):
        cat_df = compute_category_distribution(benchmark_daily_df)
        assert len(cat_df) == 6
        assert cat_df["category"].tolist() == CPCB_CATEGORIES

        # Sum of counts equals 100,794 valid days
        assert cat_df["count"].sum() == 100794

        # Sum of percentages equals ~100.0%
        assert cat_df["percentage"].sum() == pytest.approx(100.0, abs=0.2)

        # Verify Moderate is the modal category (~31.2%)
        mod_row = cat_df[cat_df["category"] == "Moderate"].iloc[0]
        assert mod_row["count"] == 31478
        assert mod_row["percentage"] == pytest.approx(31.23, abs=0.1)


class TestSeasonalComparison:
    """Validate Winter vs Non-Winter elevation."""

    def test_seasonal_elevation_benchmark(self, benchmark_daily_df):
        sc = compute_seasonal_comparison(benchmark_daily_df)
        assert sc["winter_median"] == pytest.approx(335.61, abs=0.2)
        assert sc["non_winter_median"] == pytest.approx(154.00, abs=0.2)
        assert sc["absolute_diff"] == pytest.approx(181.61, abs=0.2)
        assert sc["ratio"] == pytest.approx(2.18, abs=0.05)
        assert sc["winter_days"] + sc["non_winter_days"] == 100794

        # Verify season breakdown table has 5 seasons
        by_s = sc["by_season"]
        assert len(by_s) == 5
        assert set(by_s["season"]) == {"Winter", "Summer / Pre-Monsoon", "Monsoon", "Post-Monsoon", "Transition (Feb)"}


class TestStationRankings:
    """Validate station ranking sort order and filtering."""

    def test_station_rankings(self, benchmark_daily_df):
        rankings = compute_station_rankings(benchmark_daily_df, top_n=10, min_records=100)
        top = rankings["top_polluted"]
        clean = rankings["cleanest"]

        assert len(top) == 10
        assert len(clean) == 10
        assert top.iloc[0]["median_aqi"] >= top.iloc[-1]["median_aqi"]
        assert clean.iloc[0]["median_aqi"] <= clean.iloc[-1]["median_aqi"]
        assert top.iloc[0]["median_aqi"] > clean.iloc[0]["median_aqi"]


class TestDiwaliEventAnalysis:
    """Validate event study and paired differences."""

    def test_diwali_analysis_structure(self, benchmark_daily_df):
        res = compute_diwali_event_analysis(benchmark_daily_df)
        assert "timeline" in res
        assert "yearly_paired_diff" in res
        assert "overall_paired_diff" in res
        assert "timing_cohort_summary" in res

        # 7 years covered
        yearly = res["yearly_paired_diff"]
        assert len(yearly) == 7
        assert set(yearly["year"]) == {2017, 2018, 2019, 2020, 2021, 2022, 2023}

        # Overall paired change is positive
        overall = res["overall_paired_diff"]
        assert overall["total_pairs"] > 0
        assert overall["pct_elevated"] > 70.0
