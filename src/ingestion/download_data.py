"""
Data Ingestion Module for Delhi-NCR Air Quality Analysis
=========================================================
This module handles downloading, verifying, and preparing sample data
from the CPCB-sourced repository (Vonter/india-cpcb-aqi).

License: Open Data Commons Open Database License v1.0 (ODbL-1.0)
Original Data: Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change, Govt of India.
"""

import os
import sys
import logging
import urllib.request
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Base project paths (relative to script location)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"

# Upstream URLs
AQI_DATA_URL = "https://raw.githubusercontent.com/Vonter/india-cpcb-aqi/main/data/cpcb-aqi.parquet"
AQI_RAW_FILE = DATA_RAW_DIR / "cpcb-aqi.parquet"

SAMPLE_FILE = DATA_SAMPLE_DIR / "delhi_ncr_aqi_sample.csv"

NCR_CITIES = ["Delhi", "Faridabad", "Gurugram", "Ghaziabad", "Noida"]


def download_file(url: str, dest_path: Path, force: bool = False) -> Path:
    """
    Downloads a remote file with progress reporting.
    
    Args:
        url: Remote HTTP/HTTPS URL
        dest_path: Local Path destination
        force: If True, re-downloads even if destination exists.
        
    Returns:
        Path to downloaded file.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists() and not force:
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        logger.info(f"File already exists: {dest_path} ({size_mb:.2f} MB). Skipping download.")
        return dest_path

    logger.info(f"Downloading {url} -> {dest_path}...")
    try:
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                if percent % 20 == 0:
                    sys.stdout.write(f"\rProgress: {percent}%")
                    sys.stdout.flush()

        urllib.request.urlretrieve(url, str(dest_path), reporthook=reporthook)
        print()  # Newline after progress
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        logger.info(f"Download complete: {dest_path.name} ({size_mb:.2f} MB)")
        return dest_path
    except Exception as e:
        logger.error(f"Download failed for {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        raise


def verify_aqi_parquet(file_path: Path) -> dict:
    """
    Validates that the downloaded parquet file is intact and contains expected columns.
    
    Returns:
        dict of dataset metadata.
    """
    logger.info(f"Verifying parquet file: {file_path}")
    if not file_path.exists() or file_path.stat().st_size == 0:
        raise FileNotFoundError(f"Parquet file missing or empty: {file_path}")

    pq_file = pq.ParquetFile(str(file_path))
    schema = pq_file.schema
    num_rows = pq_file.metadata.num_rows

    expected_cols = ["Station ID", "State", "City", "Station Name", "Date"]
    col_names = [schema.column(i).name for i in range(len(schema))]
    for col in expected_cols:
        if col not in col_names:
            raise ValueError(f"Missing expected column '{col}' in parquet schema.")

    logger.info(f"Verification successful: {num_rows:,} total rows across {len(col_names)} columns.")
    return {
        "num_rows": num_rows,
        "num_columns": len(col_names),
        "columns": col_names,
        "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
    }


def create_sample_dataset(raw_parquet_path: Path, sample_output_path: Path, ncr_only: bool = True) -> Path:
    """
    Creates a compact, reproducible sample dataset (CSV format) for quick testing,
    code walkthroughs, and repository demonstration without needing large files.
    """
    logger.info("Generating representative sample dataset...")
    df = pd.read_parquet(raw_parquet_path)

    if ncr_only:
        df_filtered = df[df["City"].isin(NCR_CITIES)].copy()
    else:
        df_filtered = df.copy()

    # Stratified sample: select 2 records per (City, Station Name, Year) preserving all columns
    df_filtered["Year"] = pd.to_datetime(df_filtered["Date"]).dt.year
    sample_df = (
        df_filtered.groupby(["City", "Station Name", "Year"], group_keys=False)
        .head(2)
        .reset_index(drop=True)
    )

    if "Year" in sample_df.columns:
        sample_df = sample_df.drop(columns=["Year"])

    sample_output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(sample_output_path, index=False)
    logger.info(f"Sample dataset saved to {sample_output_path} ({len(sample_df)} rows, {sample_output_path.stat().st_size / 1024:.1f} KB).")
    return sample_output_path


def main():
    """Main execution entry point."""
    logger.info("=== Starting Data Ingestion Pipeline ===")
    downloaded_file = download_file(AQI_DATA_URL, AQI_RAW_FILE)
    meta = verify_aqi_parquet(downloaded_file)
    logger.info(f"Metadata: {meta}")

    create_sample_dataset(downloaded_file, SAMPLE_FILE)
    logger.info("=== Ingestion and Sample Preparation Completed Successfully ===")


if __name__ == "__main__":
    main()
