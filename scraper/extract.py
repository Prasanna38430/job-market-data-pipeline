"""Pulls remote job listings from the Remotive API and saves the raw response."""

import os
import json
from datetime import datetime

import requests

from scraper.logger import get_logger

log = get_logger("extract")

API_URL = "https://remotive.com/api/remote-jobs"
RAW_DIR = os.path.join("data", "raw")
HEADERS = {"User-Agent": "job-market-scraper/1.0"}


def extract(limit=100):
    """Pull remote jobs from the remotive api and save the raw response.

    Returns the list of job dicts, or an empty list if the request failed.
    """
    params = {"limit": limit}

    try:
        resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        log.error(f"request to remotive failed: {e}")
        return []
    except ValueError as e:
        # response wasn't valid json
        log.error(f"could not parse remotive response as json: {e}")
        return []

    jobs = payload.get("jobs", [])
    log.info(f"fetched {len(jobs)} jobs from remotive")

    _save_raw(payload)
    return jobs


def _save_raw(payload):
    """Save the API response to its own timestamped file so each run keeps a copy."""
    os.makedirs(RAW_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(RAW_DIR, f"jobs_raw_{timestamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    log.info(f"saved raw response to {path}")
