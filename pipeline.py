import argparse
import time

from scraper.extract import extract
from scraper.transform import transform
from scraper.load import load
from scraper.logger import get_logger

log = get_logger("pipeline")


def run(limit=100):
    start = time.time()

    raw_jobs = extract(limit=limit)
    df = transform(raw_jobs)
    load(df)

    elapsed = time.time() - start
    log.info(f"pipeline finished in {elapsed:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Run the job market ETL pipeline")
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="how many jobs to fetch from remotive (default 100)",
    )
    args = parser.parse_args()
    run(limit=args.limit)


if __name__ == "__main__":
    main()
