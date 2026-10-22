"""
dashboard/data_access.py
========================
High-performance, dual-mode data access layer for the Delhi-NCR Air Quality Dashboard.

Features:
- Dual-mode data sourcing:
  1. Primary: Local PostgreSQL database `delhi_aqi` via SQLAlchemy engine.
  2. Fallback: High-speed Apache Parquet files in `data/processed/`.
- Streamlit `@st.cache_data` caching with zero-crash fallback outside Streamlit runtimes.
- Clear data connection provenance badge (source name, record counts, host).
"""

import os
from pathlib import Path
from typing import Dict, Tuple, Any, Optional
import pandas as pd
from dotenv import load_dotenv

# Try importing Streamlit's cache_data decorator; fallback to identity decorator if absent
try:
    import streamlit as st
    cache_data = st.cache_data
except (ImportError, Exception):
    def cache_data(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Resolve Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def get_db_credentials() -> Dict[str, Any]:
    """Retrieve database connection settings from environment or default local config."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "dbname": os.getenv("DB_NAME", "delhi_aqi"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "1234"),
    }


def try_load_from_postgres() -> Optional[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
    """
    Attempt to load datasets from the local PostgreSQL database using SQLAlchemy.

    Returns
    -------
    tuple of (df_daily, df_stations, df_dates, df_diurnal) or None if connection fails.
    """
    try:
        from sqlalchemy import create_engine
        creds = get_db_credentials()
        conn_str = f"postgresql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['dbname']}"
        engine = create_engine(conn_str, connect_args={"connect_timeout": 3})

        # 1. Fact Daily AQI joined with dimensions
        daily_query = """
        SELECT
            f.station_key,
            s.raw_station_id,
            s.station_name,
            s.city,
            s.state,
            s.agency,
            f.calendar_date AS date,
            f.total_hours,
            f.valid_hours_count,
            f.missing_hours_count,
            f.capped_hours_count,
            f.anomalous_hours_count,
            f.daily_mean_aqi,
            f.daily_median_aqi,
            f.daily_min_aqi,
            f.daily_max_aqi,
            d.year,
            d.month,
            d.day,
            f.season,
            f.is_winter,
            f.is_diwali_window,
            f.diwali_relative_day,
            f.is_day_valid,
            f.daily_category
        FROM fact_daily_aqi f
        JOIN dim_station s ON f.station_key = s.station_key
        JOIN dim_date d ON f.calendar_date = d.calendar_date
        ORDER BY f.calendar_date, f.station_key;
        """
        df_daily = pd.read_sql(daily_query, engine)
        df_daily["date"] = pd.to_datetime(df_daily["date"])

        # 2. Dim Station
        station_query = "SELECT * FROM dim_station ORDER BY city, station_name;"
        df_stations = pd.read_sql(station_query, engine)

        # 3. Dim Date
        date_query = "SELECT * FROM dim_date ORDER BY calendar_date;"
        df_dates = pd.read_sql(date_query, engine)
        df_dates["calendar_date"] = pd.to_datetime(df_dates["calendar_date"])

        # 4. Hourly Diurnal Profile: check if pre-aggregated table exists or load from parquet
        diurnal_parquet = PROCESSED_DATA_DIR / "agg_hourly_diurnal.parquet"
        if diurnal_parquet.exists():
            df_diurnal = pd.read_parquet(diurnal_parquet)
        else:
            df_diurnal = pd.DataFrame()

        return df_daily, df_stations, df_dates, df_diurnal

    except Exception:
        return None


def load_from_parquet() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load datasets from pre-processed Parquet files in data/processed/.

    Returns
    -------
    tuple of (df_daily, df_stations, df_dates, df_diurnal)
    """
    daily_file = PROCESSED_DATA_DIR / "fact_daily_aqi.parquet"
    station_file = PROCESSED_DATA_DIR / "dim_station.parquet"
    date_file = PROCESSED_DATA_DIR / "dim_date.parquet"
    diurnal_file = PROCESSED_DATA_DIR / "agg_hourly_diurnal.parquet"

    if not daily_file.exists():
        raise FileNotFoundError(f"Missing required processed dataset: {daily_file}")

    df_daily = pd.read_parquet(daily_file)
    df_daily["date"] = pd.to_datetime(df_daily["date"])

    df_stations = pd.read_parquet(station_file) if station_file.exists() else pd.DataFrame()
    df_dates = pd.read_parquet(date_file) if date_file.exists() else pd.DataFrame()
    df_diurnal = pd.read_parquet(diurnal_file) if diurnal_file.exists() else pd.DataFrame()

    return df_daily, df_stations, df_dates, df_diurnal


@cache_data(show_spinner=False)
def load_all_dashboard_data(preferred_source: str = "auto") -> Dict[str, Any]:
    """
    Load all dashboard datasets with dual PostgreSQL / Parquet fallback.

    Parameters
    ----------
    preferred_source : str, default 'auto'
        'auto': tries PostgreSQL first, falls back to Parquet.
        'postgres': strictly tries PostgreSQL.
        'parquet': loads directly from local Parquet files.

    Returns
    -------
    dict
        Dictionary containing:
        - 'daily': fact_daily_aqi DataFrame
        - 'stations': dim_station DataFrame
        - 'dates': dim_date DataFrame
        - 'diurnal': agg_hourly_diurnal DataFrame
        - 'source_info': provenance details (source type, row count, host)
    """
    source_used = None
    df_daily = None
    df_stations = None
    df_dates = None
    df_diurnal = None

    if preferred_source in ("auto", "postgres"):
        pg_res = try_load_from_postgres()
        if pg_res is not None:
            df_daily, df_stations, df_dates, df_diurnal = pg_res
            source_used = "PostgreSQL Database (delhi_aqi @ localhost:5432)"

    if df_daily is None and preferred_source in ("auto", "parquet"):
        df_daily, df_stations, df_dates, df_diurnal = load_from_parquet()
        source_used = "Local Parquet Storage (data/processed/)"

    if df_daily is None:
        raise RuntimeError("Failed to load AQI datasets from both PostgreSQL and local Parquet storage.")

    # Ensure statutory categorical sorting
    cpcb_cats = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    if "daily_category" in df_daily.columns:
        df_daily["daily_category"] = pd.Categorical(
            df_daily["daily_category"], categories=cpcb_cats, ordered=True
        )

    source_info = {
        "source": source_used,
        "daily_rows": len(df_daily),
        "valid_days": int((df_daily["is_day_valid"] == True).sum()) if "is_day_valid" in df_daily.columns else len(df_daily),
        "stations_count": df_daily["station_key"].nunique() if "station_key" in df_daily.columns else 0,
        "cities": sorted(df_daily["city"].unique().tolist()) if "city" in df_daily.columns else [],
        "min_date": str(df_daily["date"].min().date()) if "date" in df_daily.columns else "",
        "max_date": str(df_daily["date"].max().date()) if "date" in df_daily.columns else "",
    }

    return {
        "daily": df_daily,
        "stations": df_stations,
        "dates": df_dates,
        "diurnal": df_diurnal,
        "source_info": source_info,
    }
