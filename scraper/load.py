"""Saves the clean jobs into SQLite, skipping ones we already have from earlier runs."""

import os
import sqlite3

from scraper.logger import get_logger

log = get_logger("load")

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
    """Insert new jobs into sqlite (incremental) and return the full table as a DataFrame.

    SQLite is the source of truth here - it handles dedup across runs. The file
    and database exports work off the table we read back at the end.
    """
    import pandas as pd

    if df.empty:
        log.info("empty dataframe, nothing to load")
        return df

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

        full = pd.read_sql_query("SELECT * FROM jobs", conn)
    finally:
        conn.close()

    return full
