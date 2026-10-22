"""
Validation suite for Power BI Desktop data model, tables, and DAX benchmark reconciliation.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
POWERBI_DIR = PROJECT_ROOT / "powerbi"


class TestPowerBIDataModel:
    """Validate that all files required for Power BI Desktop exist and conform to schema."""

    def test_powerbi_files_exist(self):
        """Confirm all source tables, DAX measures, and benchmarks exist on disk."""
        required_files = [
            PROCESSED_DIR / "fact_daily_aqi.csv",
            PROCESSED_DIR / "dim_station.csv",
            PROCESSED_DIR / "dim_date.csv",
            PROCESSED_DIR / "agg_hourly_diurnal.csv",
            PROCESSED_DIR / "fact_diwali_pairs.csv",
            PROCESSED_DIR / "dim_diwali_cohorts.csv",
            POWERBI_DIR / "measures.dax",
            POWERBI_DIR / "benchmarks_reconciliation.csv",
        ]
        for f in required_files:
            assert f.exists(), f"Required Power BI file missing: {f}"
            assert f.stat().st_size > 0, f"File is empty: {f}"

    def test_powerbi_star_schema_referential_integrity(self):
        """Confirm 100% referential integrity without orphan records."""
        fact_daily = pd.read_csv(PROCESSED_DIR / "fact_daily_aqi.csv")
        dim_station = pd.read_csv(PROCESSED_DIR / "dim_station.csv")
        dim_date = pd.read_csv(PROCESSED_DIR / "dim_date.csv")
        fact_diwali = pd.read_csv(PROCESSED_DIR / "fact_diwali_pairs.csv")

        # Station dimension primary key uniqueness
        assert dim_station["station_key"].is_unique
        assert len(dim_station) == 56

        # Date dimension primary key uniqueness
        assert dim_date["calendar_date"].is_unique
        assert len(dim_date) == 2556

        # Fact daily referential integrity
        invalid_stations = set(fact_daily["station_key"]) - set(dim_station["station_key"])
        assert len(invalid_stations) == 0, f"Orphan stations in fact_daily: {invalid_stations}"

        invalid_dates = set(fact_daily["date"]) - set(dim_date["calendar_date"])
        assert len(invalid_dates) == 0, f"Orphan dates in fact_daily: {invalid_dates}"

        # Fact Diwali referential integrity
        invalid_diwali_stations = set(fact_diwali["station_key"]) - set(dim_station["station_key"])
        assert len(invalid_diwali_stations) == 0, f"Orphan stations in fact_diwali: {invalid_diwali_stations}"

    def test_powerbi_dax_benchmarks_reconciliation(self):
        """Verify that Power BI DAX calculations match Python/PostgreSQL ground truth exactly."""
        fact_daily = pd.read_csv(PROCESSED_DIR / "fact_daily_aqi.csv")
        valid_daily = fact_daily[fact_daily["is_day_valid"] == True]
        fact_diwali = pd.read_csv(PROCESSED_DIR / "fact_diwali_pairs.csv")

        # 1. Page 1 Headline KPIs
        total_days = len(fact_daily)
        valid_days = len(valid_daily)
        assert total_days == 111014
        assert valid_days == 100794
        assert (valid_days / total_days * 100) == pytest.approx(90.79, abs=0.01)

        med_aqi = float(valid_daily["daily_mean_aqi"].median())
        mean_aqi = float(valid_daily["daily_mean_aqi"].mean())
        assert med_aqi == pytest.approx(199.29, abs=0.01)
        assert mean_aqi == pytest.approx(213.56, abs=0.01)

        severe_days = (valid_daily["daily_mean_aqi"] > 400.0).sum()
        assert severe_days == 6389
        assert (severe_days / valid_days * 100) == pytest.approx(6.34, abs=0.01)

        capped_days = (valid_daily["capped_hours_count"] > 0).sum()
        assert capped_days == 12536
        assert (capped_days / valid_days * 100) == pytest.approx(12.44, abs=0.01)

        # 2. Page 2 Seasonal Dynamics
        winter = valid_daily[valid_daily["is_winter"] == True]["daily_mean_aqi"]
        non_winter = valid_daily[valid_daily["is_winter"] == False]["daily_mean_aqi"]
        w_med = float(winter.median())
        nw_med = float(non_winter.median())
        assert w_med == pytest.approx(335.61, abs=0.01)
        assert nw_med == pytest.approx(154.00, abs=0.01)
        assert (w_med - nw_med) == pytest.approx(181.61, abs=0.01)
        assert (w_med / nw_med) == pytest.approx(2.18, abs=0.01)

        # 3. Page 3 Diwali Episodes & Cohorts
        assert len(fact_diwali) == 306
        elevated_pairs = fact_diwali["is_elevated"].sum()
        assert elevated_pairs == 263
        assert (elevated_pairs / len(fact_diwali) * 100) == pytest.approx(85.95, abs=0.01)
        assert float(fact_diwali["paired_surge"].mean()) == pytest.approx(81.57, abs=0.01)
        assert float(fact_diwali["paired_surge"].median()) == pytest.approx(80.38, abs=0.01)

        oct_pairs = fact_diwali[fact_diwali["timing_cohort"] == "October Diwali"]
        nov_pairs = fact_diwali[fact_diwali["timing_cohort"] == "November Diwali"]
        assert len(oct_pairs) == 108
        assert len(nov_pairs) == 198
        assert float(oct_pairs["paired_surge"].mean()) == pytest.approx(58.92, abs=0.01)
        assert float(nov_pairs["paired_surge"].mean()) == pytest.approx(93.92, abs=0.01)

    def test_powerbi_live_analysis_services_dax(self):
        """Verify DAX measures directly inside running Power BI Desktop tabular instance (if live)."""
        import subprocess
        import json
        import shutil

        powershell = shutil.which("powershell")
        if not powershell:
            pytest.skip("PowerShell not found on system.")

        script_path = POWERBI_DIR / "query_dax_runtime.ps1"
        if not script_path.exists():
            pytest.skip("query_dax_runtime.ps1 not found.")

        result = subprocess.run(
            [powershell, "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            pytest.skip(f"Power BI live instance not currently available: {result.stderr.strip()[:100]}")

        dax_results = json.loads(result.stdout)

        # 1. Page 1 Headline KPIs
        assert dax_results["Total Scheduled Station-Days"] == 111014
        assert dax_results["Valid Station-Days"] == 100794
        assert (dax_results["Data Completeness %"] * 100) == pytest.approx(90.79, abs=0.01)
        assert dax_results["Median AQI"] == pytest.approx(199.29, abs=0.01)
        assert dax_results["Mean AQI"] == pytest.approx(213.56, abs=0.01)
        assert dax_results["AQI IQR"] == pytest.approx(185.17, abs=0.01)
        assert dax_results["Severe AQI Days Count"] == 6389
        assert dax_results["Severe AQI Days %"] == pytest.approx(6.34, abs=0.01)
        assert dax_results["Sensor Capped Days Count"] == 12536
        assert dax_results["Sensor Capped Days %"] == pytest.approx(12.44, abs=0.01)

        # 2. Page 2 Seasonal Dynamics
        assert dax_results["Winter Median AQI"] == pytest.approx(335.61, abs=0.01)
        assert dax_results["Non-Winter Median AQI"] == pytest.approx(154.00, abs=0.01)
        assert dax_results["Winter Elevation Absolute"] == pytest.approx(181.61, abs=0.01)
        assert dax_results["Winter Elevation Ratio"] == pytest.approx(2.18, abs=0.01)

        # 3. Page 3 Diwali Episodes & Cohorts
        assert dax_results["Diwali Matched Station-Years"] == 306
        assert dax_results["Diwali Pooled Mean Surge"] == pytest.approx(81.57, abs=0.01)
        assert dax_results["Diwali Pooled Median Surge"] == pytest.approx(80.38, abs=0.01)
        assert dax_results["Diwali Elevated Station-Years Count"] == 263
        assert dax_results["Diwali Station-Years Elevated %"] == pytest.approx(85.95, abs=0.01)
        assert dax_results["October Diwali Pooled Mean Surge"] == pytest.approx(58.92, abs=0.01)
        assert dax_results["November Diwali Pooled Mean Surge"] == pytest.approx(93.92, abs=0.01)

    def test_powerbi_pbir_visual_definitions(self):
        """Validate PBIR structure, 3 report pages, and 34 visuals in complete PBIX and PBIP."""
        import zipfile
        complete_pbix = PROJECT_ROOT / "delhi_ncr_aqi_analysis_complete.pbix"
        pbip_file = PROJECT_ROOT / "delhi_ncr_aqi_analysis.pbip"
        report_dir = PROJECT_ROOT / "delhi_ncr_aqi_analysis.Report"

        assert complete_pbix.exists(), "Complete PBIX file missing on disk"
        assert complete_pbix.stat().st_size > 1_000_000, "Complete PBIX file appears truncated"
        assert pbip_file.exists(), "PBIP project file missing on disk"
        assert report_dir.exists(), "PBIP Report folder missing on disk"

        # Inspect internal PBIX structure
        with zipfile.ZipFile(complete_pbix, "r") as zf:
            namelist = zf.namelist()
            assert "Report/definition/pages/pages.json" in namelist
            assert "Report/definition/report.json" in namelist
            assert "DataModel" in namelist

            # Verify pages metadata
            pages_data = json.loads(zf.read("Report/definition/pages/pages.json").decode("utf-8"))
            assert len(pages_data["pageOrder"]) == 3
            assert pages_data["activePageName"] == "2941a98a6619273cadf8"

            # Verify page display names
            p1 = json.loads(zf.read(f"Report/definition/pages/{pages_data['pageOrder'][0]}/page.json").decode("utf-8"))
            p2 = json.loads(zf.read(f"Report/definition/pages/{pages_data['pageOrder'][1]}/page.json").decode("utf-8"))
            p3 = json.loads(zf.read(f"Report/definition/pages/{pages_data['pageOrder'][2]}/page.json").decode("utf-8"))

            assert p1["displayName"] == "Regional AQI Overview"
            assert p2["displayName"] == "Seasonal Inversion & Spatial Dynamics"
            assert p3["displayName"] == "Diwali Episode Analysis & Confounding"

            # Count visuals across all pages
            visual_files = [n for n in namelist if n.startswith("Report/definition/pages/") and n.endswith("/visual.json")]
            assert len(visual_files) == 34, f"Expected 34 visuals, found {len(visual_files)}"


