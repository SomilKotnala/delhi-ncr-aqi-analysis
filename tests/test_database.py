"""
Automated Pytest Suite for PostgreSQL 18 Integration & Analytical Outputs
==========================================================================
Tests:
  - Database connectivity and schema existence
  - Row counts reconciliation across all Star Schema tables
  - Foreign key referential integrity (zero orphan records)
  - Analytical query CSV deliverables in reports/tables/
  - Production EDA figure existence and non-zero size in reports/figures/
"""

import os
import sys
import json
from pathlib import Path
import pytest
import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(r"D:\delhi-ncr-aqi-analysis")
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "delhi_aqi")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


@pytest.fixture(scope="module")
def pg_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    yield conn
    conn.close()


def test_postgres_connection_and_version(pg_conn):
    cur = pg_conn.cursor()
    cur.execute("SELECT version();")
    ver = cur.fetchone()[0]
    cur.close()
    assert "PostgreSQL" in ver


def test_schema_tables_exist(pg_conn):
    expected_tables = {"dim_station", "dim_date", "fact_daily_aqi", "fact_hourly_aqi"}
    cur = pg_conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    existing_tables = {r[0] for r in cur.fetchall()}
    cur.close()
    assert expected_tables.issubset(existing_tables)


def test_row_counts_reconciliation(pg_conn):
    cur = pg_conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM dim_station;")
    station_count = cur.fetchone()[0]
    assert station_count == 56, f"Expected 56 stations, got {station_count}"

    cur.execute("SELECT COUNT(*) FROM dim_date;")
    date_count = cur.fetchone()[0]
    assert date_count == 2556, f"Expected 2,556 calendar dates, got {date_count}"

    cur.execute("SELECT COUNT(*) FROM fact_daily_aqi;")
    daily_count = cur.fetchone()[0]
    assert daily_count == 111014, f"Expected 111,014 daily rows, got {daily_count}"

    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi;")
    hourly_count = cur.fetchone()[0]
    assert hourly_count == 2664336, f"Expected 2,664,336 hourly rows, got {hourly_count}"

    cur.close()


def test_referential_integrity_no_orphans(pg_conn):
    cur = pg_conn.cursor()
    
    # Check fact_daily_aqi foreign keys
    cur.execute("""
        SELECT COUNT(*) FROM fact_daily_aqi f
        LEFT JOIN dim_station s ON f.station_key = s.station_key
        WHERE s.station_key IS NULL;
    """)
    daily_station_orphans = cur.fetchone()[0]
    assert daily_station_orphans == 0

    cur.execute("""
        SELECT COUNT(*) FROM fact_daily_aqi f
        LEFT JOIN dim_date d ON f.calendar_date = d.calendar_date
        WHERE d.calendar_date IS NULL;
    """)
    daily_date_orphans = cur.fetchone()[0]
    assert daily_date_orphans == 0

    # Check fact_hourly_aqi foreign keys
    cur.execute("""
        SELECT COUNT(*) FROM fact_hourly_aqi f
        LEFT JOIN dim_station s ON f.station_key = s.station_key
        WHERE s.station_key IS NULL;
    """)
    hourly_station_orphans = cur.fetchone()[0]
    assert hourly_station_orphans == 0

    cur.execute("""
        SELECT COUNT(*) FROM fact_hourly_aqi f
        LEFT JOIN dim_date d ON f.calendar_date = d.calendar_date
        WHERE d.calendar_date IS NULL;
    """)
    hourly_date_orphans = cur.fetchone()[0]
    assert hourly_date_orphans == 0

    cur.close()


def test_sensor_ceiling_and_anomalies_counts(pg_conn):
    cur = pg_conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi WHERE is_sensor_capped = TRUE;")
    capped_count = cur.fetchone()[0]
    assert capped_count == 53656, f"Expected 53,656 capped records, got {capped_count}"

    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi WHERE is_anomalous = TRUE;")
    anom_count = cur.fetchone()[0]
    assert anom_count == 10, f"Expected 10 anomalous records, got {anom_count}"

    cur.close()


def test_analytical_query_outputs_exist():
    tables_dir = PROJECT_ROOT / "reports" / "tables"
    expected_files = [
        "q1_executive_kpi_summary.csv",
        "q2_monthly_trends_seasonal_inversion_wave_research_question_1.csv",
        "q3_station_rankings_spatial_heterogeneity_research_question_2.csv",
        "q4_severity_category_distribution_by_season_and_city_research_question_3.csv",
        "q5_diurnal_diurnal_profiling_research_question_6.csv",
        "q6_diwali_event_study_trajectory_research_question_8.csv",
        "q7_station_completeness_sensor_capping_audit_research_question_7.csv",
        "analytical_queries_results.json",
        "database_verification_metrics.json"
    ]
    for fn in expected_files:
        fp = tables_dir / fn
        assert fp.exists() and fp.stat().st_size > 0, f"Missing or empty deliverable: {fn}"


def test_eda_figures_exist():
    figures_dir = PROJECT_ROOT / "reports" / "figures"
    expected_figures = [
        "q1_monthly_seasonal_trends.png",
        "q2_station_rankings.png",
        "q3_severity_distribution.png",
        "q5_diurnal_hourly_patterns.png",
        "q6_diwali_event_study.png",
        "q7_station_uptime_vs_capping.png"
    ]
    for fn in expected_figures:
        fp = figures_dir / fn
        assert fp.exists() and fp.stat().st_size > 10000, f"Missing or incomplete figure: {fn}"
