"""
Database Loader Module: PostgreSQL 18 Integration
==================================================
This module connects to the local PostgreSQL instance, provisions the
`delhi_aqi` database on the high-capacity D: drive tablespace (protecting C: drive),
applies the Star Schema DDL, loads the processed dimensional and fact tables
via high-speed streaming COPY, builds indexes, and runs integrity verifications.

Outputs:
  - Tables populated in `delhi_aqi`: dim_station, dim_date, fact_daily_aqi, fact_hourly_aqi
  - Verification audit log: reports/tables/database_verification_metrics.json
"""

import io
import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Base project paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"

# Load local environment variables from .env
load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "delhi_aqi")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

TABLESPACE_NAME = "aqi_tablespace"
TABLESPACE_DIR = Path(r"D:\pg_tablespaces\delhi_aqi")

DIWALI_DATES = {
    2017: pd.Timestamp("2017-10-19"),
    2018: pd.Timestamp("2018-11-07"),
    2019: pd.Timestamp("2019-10-27"),
    2020: pd.Timestamp("2020-11-14"),
    2021: pd.Timestamp("2021-11-04"),
    2022: pd.Timestamp("2022-10-24"),
    2023: pd.Timestamp("2023-11-12"),
}


def get_connection(dbname: str = DB_NAME) -> psycopg2.extensions.connection:
    """Creates a connection to PostgreSQL protecting credentials."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=dbname
    )


def ensure_tablespace_and_database() -> None:
    """
    Ensures `aqi_tablespace` exists on D: drive (protecting C: drive)
    and `delhi_aqi` database exists. Does NOT alter any other database.
    """
    logger.info("Verifying tablespace and database configuration...")
    TABLESPACE_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = get_connection(dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # 1. Tablespace
    cur.execute("SELECT spcname FROM pg_tablespace WHERE spcname = %s;", (TABLESPACE_NAME,))
    if not cur.fetchone():
        ts_loc = str(TABLESPACE_DIR).replace("\\", "/")
        logger.info(f"Creating tablespace '{TABLESPACE_NAME}' at {ts_loc}...")
        cur.execute(f"CREATE TABLESPACE {TABLESPACE_NAME} LOCATION '{ts_loc}';")
        logger.info("Tablespace created successfully.")
    else:
        logger.info(f"Tablespace '{TABLESPACE_NAME}' verified on D: drive.")

    # 2. Database
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
    if not cur.fetchone():
        logger.info(f"Creating database '{DB_NAME}' with tablespace '{TABLESPACE_NAME}'...")
        cur.execute(f"CREATE DATABASE {DB_NAME} TABLESPACE {TABLESPACE_NAME};")
        logger.info(f"Database '{DB_NAME}' created successfully.")
    else:
        logger.info(f"Database '{DB_NAME}' already exists.")

    cur.close()
    conn.close()


def apply_schema(schema_path: Path = SQL_DIR / "schema.sql") -> None:
    """Executes the DDL schema script in `delhi_aqi`."""
    logger.info(f"Applying Star Schema DDL from {schema_path}...")
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        ddl = f.read()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(ddl)
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Star Schema tables and indexes created successfully.")


def generate_dim_date(start_date: str = "2017-01-01", end_date: str = "2023-12-31") -> pd.DataFrame:
    """Generates the calendar date dimension table for the 7-year horizon."""
    logger.info(f"Generating date dimension: {start_date} to {end_date}...")
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    def assign_season(month: int) -> str:
        if month in (11, 12, 1):
            return "Winter"
        elif month in (3, 4, 5):
            return "Summer / Pre-Monsoon"
        elif month in (6, 7, 8, 9):
            return "Monsoon"
        elif month == 10:
            return "Post-Monsoon"
        elif month == 2:
            return "Transition (Feb)"
        return "Unknown"

    records = []
    for d in date_range:
        yr = d.year
        mo = d.month
        diwali_dt = DIWALI_DATES.get(yr)
        if diwali_dt is not None:
            delta = (d - diwali_dt).days
            is_diwali = -7 <= delta <= 7
            rel_day = int(delta) if is_diwali else None
        else:
            is_diwali = False
            rel_day = None

        records.append({
            "calendar_date": d.strftime("%Y-%m-%d"),
            "year": yr,
            "month": mo,
            "month_name": d.strftime("%B"),
            "day": d.day,
            "day_of_week": d.weekday(),
            "day_name": d.strftime("%A"),
            "is_weekend": d.weekday() in (5, 6),
            "season": assign_season(mo),
            "is_winter": mo in (11, 12, 1),
            "is_diwali_window": is_diwali,
            "diwali_relative_day": rel_day
        })

    return pd.DataFrame(records)


def copy_dataframe(conn, df: pd.DataFrame, table_name: str, columns: List[str]) -> None:
    """Performs high-speed streaming COPY of a DataFrame into PostgreSQL."""
    cur = conn.cursor()
    buffer = io.StringIO()
    df_copy = df[columns].copy()

    # Format nullable smallints explicitly
    if "diwali_relative_day" in df_copy.columns:
        df_copy["diwali_relative_day"] = df_copy["diwali_relative_day"].apply(
            lambda v: "\\N" if pd.isna(v) else str(int(round(float(v))))
        )

    df_copy.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N")
    buffer.seek(0)
    
    col_str = ", ".join(f'"{c}"' for c in columns)
    copy_sql = f'COPY "{table_name}" ({col_str}) FROM STDIN WITH (FORMAT csv, DELIMITER "\t", NULL "\\N")'
    cur.copy_expert(copy_sql, buffer)
    cur.close()


def load_all_data() -> Dict[str, Any]:
    """Orchestrates loading dim_station, dim_date, fact_daily_aqi, and fact_hourly_aqi."""
    t0 = time.time()
    ensure_tablespace_and_database()
    apply_schema()

    conn = get_connection()

    # 1. Load dim_station
    logger.info("Loading dim_station...")
    dim_station_path = DATA_PROCESSED_DIR / "dim_station.csv"
    if not dim_station_path.exists():
        raise FileNotFoundError(f"Missing {dim_station_path}")
    df_station = pd.read_csv(dim_station_path)
    
    station_cols = [
        "station_key", "raw_station_id", "station_name", "city", "state", "agency",
        "first_record_date", "last_record_date", "total_recorded_days",
        "total_hourly_records", "valid_hourly_records", "missing_hourly_records",
        "uptime_hourly_pct", "temporal_coverage_pct", "capped_hours_pct",
        "mean_aqi", "median_aqi"
    ]
    copy_dataframe(conn, df_station, "dim_station", station_cols)
    conn.commit()
    logger.info(f"Loaded {len(df_station)} rows into dim_station.")

    # 2. Load dim_date
    logger.info("Loading dim_date...")
    df_date = generate_dim_date()
    date_cols = [
        "calendar_date", "year", "month", "month_name", "day", "day_of_week",
        "day_name", "is_weekend", "season", "is_winter", "is_diwali_window",
        "diwali_relative_day"
    ]
    copy_dataframe(conn, df_date, "dim_date", date_cols)
    conn.commit()
    logger.info(f"Loaded {len(df_date)} rows into dim_date.")

    # 3. Load fact_daily_aqi
    logger.info("Loading fact_daily_aqi from Parquet...")
    daily_path = DATA_PROCESSED_DIR / "fact_daily_aqi.parquet"
    if not daily_path.exists():
        raise FileNotFoundError(f"Missing {daily_path}")
    df_daily = pd.read_parquet(daily_path)
    df_daily["calendar_date"] = pd.to_datetime(df_daily["date"]).dt.strftime("%Y-%m-%d")

    daily_cols = [
        "station_key", "calendar_date", "total_hours", "valid_hours_count",
        "missing_hours_count", "capped_hours_count", "anomalous_hours_count",
        "is_day_valid", "daily_mean_aqi", "daily_median_aqi", "daily_min_aqi",
        "daily_max_aqi", "daily_category", "season", "is_winter",
        "is_diwali_window", "diwali_relative_day"
    ]
    copy_dataframe(conn, df_daily, "fact_daily_aqi", daily_cols)
    conn.commit()
    logger.info(f"Loaded {len(df_daily):,} rows into fact_daily_aqi.")

    # 4. Load fact_hourly_aqi (Streamed in chunks for speed and low memory)
    logger.info("Loading fact_hourly_aqi from Parquet (streaming 2.66M rows)...")
    hourly_path = DATA_PROCESSED_DIR / "fact_hourly_aqi.parquet"
    if not hourly_path.exists():
        raise FileNotFoundError(f"Missing {hourly_path}")

    # Read Parquet
    df_hourly = pd.read_parquet(hourly_path)
    # Extract string dates for calendar_date foreign key
    df_hourly["calendar_date"] = pd.to_datetime(df_hourly["date"]).dt.strftime("%Y-%m-%d")

    hourly_cols = [
        "station_key", "calendar_date", "timestamp_ist", "timestamp_utc",
        "hour", "aqi_raw", "aqi_cleaned", "aqi_category", "is_missing",
        "is_sensor_capped", "is_anomalous", "is_valid"
    ]

    chunk_size = 500_000
    total_hourly_rows = len(df_hourly)
    for start_idx in range(0, total_hourly_rows, chunk_size):
        end_idx = min(start_idx + chunk_size, total_hourly_rows)
        chunk = df_hourly.iloc[start_idx:end_idx]
        copy_dataframe(conn, chunk, "fact_hourly_aqi", hourly_cols)
        conn.commit()
        pct = round(end_idx / total_hourly_rows * 100, 1)
        logger.info(f"Streamed {end_idx:,}/{total_hourly_rows:,} rows ({pct}%) into fact_hourly_aqi...")

    conn.close()
    elapsed = round(time.time() - t0, 2)
    logger.info(f"Data loading complete in {elapsed}s.")
    return {"elapsed_seconds": elapsed}


def verify_database() -> Dict[str, Any]:
    """Runs verification queries to confirm row counts, keys, ranges, and referential integrity."""
    logger.info("Verifying PostgreSQL database integrity...")
    conn = get_connection()
    cur = conn.cursor()

    verification = {}

    # 1. Table row counts
    cur.execute("SELECT COUNT(*) FROM dim_station;")
    verification["dim_station_count"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM dim_date;")
    verification["dim_date_count"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_daily_aqi;")
    verification["fact_daily_count"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi;")
    verification["fact_hourly_count"] = cur.fetchone()[0]

    # 2. Date ranges
    cur.execute("SELECT MIN(calendar_date), MAX(calendar_date) FROM fact_daily_aqi;")
    dmin, dmax = cur.fetchone()
    verification["min_daily_date"] = str(dmin)
    verification["max_daily_date"] = str(dmax)

    # 3. Unique station keys in fact tables
    cur.execute("SELECT COUNT(DISTINCT station_key) FROM fact_daily_aqi;")
    verification["fact_daily_stations"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT station_key) FROM fact_hourly_aqi;")
    verification["fact_hourly_stations"] = cur.fetchone()[0]

    # 4. Foreign key integrity / orphan check
    cur.execute("""
        SELECT COUNT(*) FROM fact_daily_aqi f
        LEFT JOIN dim_station s ON f.station_key = s.station_key
        WHERE s.station_key IS NULL;
    """)
    verification["daily_orphan_stations"] = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM fact_hourly_aqi f
        LEFT JOIN dim_station s ON f.station_key = s.station_key
        WHERE s.station_key IS NULL;
    """)
    verification["hourly_orphan_stations"] = cur.fetchone()[0]

    # 5. Capped records and anomalous records check
    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi WHERE is_sensor_capped = TRUE;")
    verification["db_sensor_capped_count"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi WHERE is_anomalous = TRUE;")
    verification["db_anomalous_count"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi WHERE is_valid = TRUE;")
    verification["db_valid_hourly_count"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_hourly_aqi WHERE is_missing = TRUE;")
    verification["db_missing_hourly_count"] = cur.fetchone()[0]

    cur.close()
    conn.close()

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    report_file = TABLES_DIR / "database_verification_metrics.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(verification, f, indent=2)

    logger.info(f"Database verification report saved to {report_file.name}: {verification}")
    return verification


def main():
    """Execution entry point."""
    logger.info("=== Starting PostgreSQL 18 Star Schema Data Loader ===")
    load_all_data()
    verification = verify_database()
    print("\nDatabase Verification Summary:")
    for k, v in verification.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
