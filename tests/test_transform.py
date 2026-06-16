"""Tests for the transform step. Run with: python -m pytest  (or just python tests/test_transform.py)"""

import os
import sys

# let the test find the scraper package when run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraper.transform import transform


def sample_jobs():
    return [
        {
            "id": 1,
            "url": "https://example.com/1",
            "title": "  Python Developer  ",
            "company_name": "Acme",
            "category": "Software Development",
            "tags": ["python", "sql"],
            "job_type": "full_time",
            "publication_date": "2026-06-10T12:00:00",
            "candidate_required_location": "Worldwide",
            "salary": "",
        },
        # same id as above, should be dropped as a duplicate
        {
            "id": 1,
            "url": "https://example.com/1",
            "title": "Python Developer",
            "company_name": "Acme",
            "category": "Software Development",
            "tags": ["python"],
            "job_type": "full_time",
            "publication_date": "2026-06-10T12:00:00",
            "candidate_required_location": "Worldwide",
            "salary": "",
        },
        # missing company name, should be dropped
        {
            "id": 2,
            "url": "https://example.com/2",
            "title": "Data Analyst",
            "company_name": None,
            "category": "Data",
            "tags": ["sql"],
            "job_type": "contract",
            "publication_date": "2026-06-11T12:00:00",
            "candidate_required_location": "US",
            "salary": "50000",
        },
    ]


def test_dedup_and_drop():
    df = transform(sample_jobs())
    # one duplicate and one incomplete row removed, leaving a single job
    assert len(df) == 1
    assert df.iloc[0]["id"] == 1


def test_columns_renamed():
    df = transform(sample_jobs())
    assert "job_title" in df.columns
    assert "location" in df.columns
    assert "posted_date" in df.columns
    assert "title" not in df.columns


def test_whitespace_stripped():
    df = transform(sample_jobs())
    assert df.iloc[0]["job_title"] == "Python Developer"


def test_tags_become_string():
    df = transform(sample_jobs())
    assert df.iloc[0]["tags"] == "python, sql"


def test_empty_salary_is_null():
    df = transform(sample_jobs())
    assert df.iloc[0]["salary"] is None


def test_date_formatted():
    df = transform(sample_jobs())
    assert df.iloc[0]["posted_date"] == "2026-06-10"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok - {t.__name__}")
    print(f"\nall {len(tests)} tests passed")
