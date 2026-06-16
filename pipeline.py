"""Runs the whole pipeline end to end: extract, transform, load, then export."""

import argparse
import time

from scraper.extract import extract
from scraper.transform import transform
from scraper.load import load
from scraper.export import export_files, VALID_FORMATS
from scraper.logger import get_logger

log = get_logger("pipeline")


def run(limit=100, formats=("csv",), db=None):
    """Run the pipeline once: fetch jobs, clean them, store them, and export."""
    start = time.time()

    raw_jobs = extract(limit=limit)
    df = transform(raw_jobs)
    full = load(df)

    export_files(full, formats)

    if db:
        # imported here so the base pipeline runs even without the db drivers installed
        from scraper.database import export_to_database
        export_to_database(full, db)

    elapsed = time.time() - start
    log.info(f"pipeline finished in {elapsed:.1f}s")


def parse_formats(value):
    """Turn the --format string into a clean list and reject anything we don't support."""
    formats = [f.strip().lower() for f in value.split(",") if f.strip()]
    bad = [f for f in formats if f not in VALID_FORMATS]
    if bad:
        raise argparse.ArgumentTypeError(
            f"unsupported format(s): {', '.join(bad)}. pick from {', '.join(VALID_FORMATS)}"
        )
    return formats


def main():
    parser = argparse.ArgumentParser(description="Run the job market ETL pipeline")
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="how many jobs to fetch from remotive (default 100)",
    )
    parser.add_argument(
        "--format",
        type=parse_formats,
        default=["csv"],
        help="output file formats, comma separated: csv, parquet, json (default csv)",
    )
    parser.add_argument(
        "--db",
        choices=["postgres", "mysql"],
        help="also push the clean table to an external database",
    )
    args = parser.parse_args()
    run(limit=args.limit, formats=args.format, db=args.db)


if __name__ == "__main__":
    main()
