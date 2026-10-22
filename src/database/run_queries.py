"""
Analytical Query Runner: PostgreSQL 18
=======================================
Executes all 7 analytical queries against the PostgreSQL `delhi_aqi` database,
measures execution times, and exports the results to CSV and JSON in `reports/tables/`.
"""

import os
import re
import time
import json
import logging
from pathlib import Path
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(r"D:\delhi-ncr-aqi-analysis")
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"

load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "delhi_aqi")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )


def extract_queries_from_file(sql_file_path: Path):
    with open(sql_file_path, "r", encoding="utf-8") as f:
        text = f.read()

    headers = re.findall(r"-- Query (\d+):([^\n]+)", text)
    blocks = re.split(r"-- Query \d+:[^\n]+", text)[1:]

    queries = []
    for (num_str, title), block in zip(headers, blocks):
        lines = block.strip().splitlines()
        sql_lines = [l for l in lines if not l.strip().startswith("--")]
        sql_code = "\n".join(sql_lines).strip()
        if sql_code:
            queries.append({
                "number": int(num_str),
                "title": title.strip(),
                "sql": sql_code
            })
    return sorted(queries, key=lambda x: x["number"])


def run_all():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    sql_file = SQL_DIR / "analytical_queries.sql"
    queries = extract_queries_from_file(sql_file)
    logger.info(f"Identified {len(queries)} analytical queries in {sql_file.name}.")

    conn = get_connection()
    summary = []

    for q in queries:
        num = q["number"]
        title = q["title"]
        logger.info(f"Running Query {num}: {title}...")
        t0 = time.time()
        
        cur = conn.cursor()
        cur.execute(q["sql"])
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=cols)
        cur.close()
        
        elapsed = round(time.time() - t0, 3)
        logger.info(f"Query {num} completed in {elapsed}s ({len(df)} rows).")

        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        out_csv = TABLES_DIR / f"q{num}_{slug}.csv"
        df.to_csv(out_csv, index=False)

        summary.append({
            "query_number": num,
            "title": title,
            "elapsed_seconds": elapsed,
            "rows_returned": len(df),
            "csv_file": out_csv.name,
            "sample_records": df.head(5).to_dict(orient="records")
        })

    conn.close()

    summary_file = TABLES_DIR / "analytical_queries_results.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info(f"Saved complete execution summary to {summary_file.name}.")

    print("\n=== Analytical Queries Execution Summary ===")
    for s in summary:
        print(f"Query {s['query_number']}: {s['title']} -> {s['rows_returned']} rows ({s['elapsed_seconds']}s) -> {s['csv_file']}")


if __name__ == "__main__":
    run_all()
