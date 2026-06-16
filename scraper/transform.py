"""Cleans the raw job data and gets it into a tidy table ready to store."""

from datetime import datetime

import pandas as pd

from scraper.logger import get_logger

log = get_logger("transform")

KEEP_COLUMNS = [
    "id",
    "url",
    "title",
    "company_name",
    "category",
    "tags",
    "job_type",
    "publication_date",
    "candidate_required_location",
    "salary",
]

RENAME = {
    "title": "job_title",
    "candidate_required_location": "location",
    "publication_date": "posted_date",
}


def transform(raw_jobs):
    """Clean the raw job list and return a tidy DataFrame ready for loading."""
    if not raw_jobs:
        log.info("no jobs to transform")
        return pd.DataFrame()

    df = pd.DataFrame(raw_jobs)

    # some runs may be missing a column entirely, fill it so the reindex is safe
    df = df.reindex(columns=KEEP_COLUMNS)
    df = df.rename(columns=RENAME)

    df["tags"] = df["tags"].apply(_tags_to_string)

    string_cols = [c for c in df.columns if c != "id"]
    for col in string_cols:
        df[col] = df[col].apply(_strip)

    df["posted_date"] = pd.to_datetime(df["posted_date"], errors="coerce", utc=True)
    df["posted_date"] = df["posted_date"].dt.strftime("%Y-%m-%d")

    # empty salary should be a real null, not an empty string
    df["salary"] = df["salary"].replace("", None)

    df["scraped_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    before = len(df)
    df = df.drop_duplicates(subset="id", keep="first")
    df = df.dropna(subset=["job_title", "company_name"])
    dropped = before - len(df)
    if dropped:
        log.info(f"dropped {dropped} duplicate or incomplete rows")

    log.info(f"transformed {len(df)} clean job records")
    return df


def _tags_to_string(tags):
    if isinstance(tags, list):
        return ", ".join(str(t).strip() for t in tags if t)
    return tags


def _strip(value):
    if isinstance(value, str):
        return value.strip()
    return value
