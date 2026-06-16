"""Writes the clean table out to csv, parquet, or json."""

import os

from scraper.logger import get_logger

log = get_logger("export")

PROCESSED_DIR = os.path.join("data", "processed")
BASENAME = "jobs_clean"

VALID_FORMATS = ("csv", "parquet", "json")


def export_files(df, formats, out_dir=PROCESSED_DIR):
    """Write the clean table to each requested file format (csv, parquet, json)."""
    if df.empty:
        log.info("empty dataframe, nothing to export")
        return

    os.makedirs(out_dir, exist_ok=True)
    for fmt in formats:
        path = os.path.join(out_dir, f"{BASENAME}.{fmt}")
        try:
            _write(df, fmt, path)
            log.info(f"exported {len(df)} rows to {path}")
        except ImportError:
            # parquet needs pyarrow, which is optional
            log.error(f"cannot write {fmt}, missing dependency (parquet needs pyarrow)")
        except Exception as e:
            log.error(f"failed to write {fmt}: {e}")


def _write(df, fmt, path):
    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "parquet":
        df.to_parquet(path, index=False)
    elif fmt == "json":
        df.to_json(path, orient="records", indent=2)
    else:
        raise ValueError(f"unknown format: {fmt}")
