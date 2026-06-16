import os
import sqlite3

from scraper.logger import get_logger

log = get_logger("load")

PROCESSED_DIR = os.path.join("data", "processed")
CSV_PATH = os.path.join(PROCESSED_DIR, "jobs_clean.csv")

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    url TEXT,
    job_title TEXT,
    company_name TEXT,
    category TEXT,
    tags TEXT,
    job_type TEXT,
    posted_date TEXT,
    location TEXT,
    salary TEXT,
    scraped_at TEXT
)
"""

COLUMNS = [
    "id",
    "url",
    "job_title",
    "company_name",
    "category",
    "tags",
    "job_type",
    "posted_date",
    "location",
    "salary",
    "scraped_at",
]


def load(df, db_path="data/jobs.db"):
    """Insert new jobs into sqlite (incremental) and export the full table to csv."""
    if df.empty:
        log.info("empty dataframe, nothing to load")
        return

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(CREATE_TABLE)

        existing = {row[0] for row in conn.execute("SELECT id FROM jobs")}
        new_rows = df[~df["id"].isin(existing)]
        skipped = len(df) - len(new_rows)

        if not new_rows.empty:
            records = new_rows[COLUMNS].itertuples(index=False, name=None)
            placeholders = ", ".join(["?"] * len(COLUMNS))
            conn.executemany(
                f"INSERT INTO jobs ({', '.join(COLUMNS)}) VALUES ({placeholders})",
                records,
            )
            conn.commit()

        log.info(f"inserted {len(new_rows)} new records, skipped {skipped} existing")

        _export_csv(conn)
    finally:
        conn.close()


def _export_csv(conn):
    import pandas as pd

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    full = pd.read_sql_query("SELECT * FROM jobs", conn)
    full.to_csv(CSV_PATH, index=False)
    log.info(f"exported {len(full)} rows to {CSV_PATH}")
