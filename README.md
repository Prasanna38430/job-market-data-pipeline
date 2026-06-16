# Job Market Analytics Pipeline

A Python ETL pipeline that pulls remote job listings from Remotive,
cleans the data, and loads it into a local SQLite database for analysis.

Built as a portfolio project to demonstrate end-to-end data pipeline
skills — extraction, transformation, loading, and analytics.

## What it does

The pipeline runs in four stages. First it **extracts** remote job
listings from the Remotive public API and saves the raw JSON so every
run is reproducible. Then it **transforms** the data with Pandas —
renaming fields, stripping whitespace, flattening the tags list, parsing
dates, and dropping duplicates and incomplete rows. Next it **loads** the
clean records into a SQLite table, only inserting jobs it hasn't seen
before, and exports the full table to a CSV. Finally `analytics.py`
runs a set of queries against the database to show what the job market
looks like.

## Tech stack

- Python 3.x
- Requests (HTTP calls)
- Pandas (data cleaning)
- SQLite (local storage)
- Logging (pipeline monitoring)

## How to run

```bash
# 1. get the code
git clone <your-repo-url>
cd job-market-scraper

# 2. set up a virtual environment and install deps
python -m venv .venv
.venv\Scripts\activate        # on Windows
source .venv/bin/activate     # on mac/linux
pip install -r requirements.txt

# 3. run the full pipeline (fetches 100 jobs by default)
python pipeline.py

# fetch a different number of jobs
python pipeline.py --limit 250

# 4. run the analytics
python analytics.py
```

## Project structure

```
job-market-scraper/
├── scraper/
│   ├── __init__.py
│   ├── logger.py      shared logging config (console + file)
│   ├── extract.py     calls the Remotive API, saves raw JSON
│   ├── transform.py   cleans and dedupes the data with Pandas
│   └── load.py        inserts into SQLite, exports CSV
├── analytics.py       runs the analytics queries and prints results
├── pipeline.py        runs extract -> transform -> load end to end
├── data/
│   ├── raw/           raw JSON responses, one file per run
│   ├── processed/     jobs_clean.csv export
│   └── jobs.db        SQLite database (created at runtime)
├── logs/              pipeline.log
├── requirements.txt
├── .gitignore
└── README.md
```

## Sample output

`data/processed/jobs_clean.csv` has one row per job with columns like
`id, url, job_title, company_name, category, tags, job_type,
posted_date, location, salary, scraped_at`. A row looks roughly like:

```
id,job_title,company_name,category,tags,job_type,posted_date,location
1234,Senior Python Engineer,Acme Remote,Software Development,"python, django, aws",full_time,2026-06-14,Worldwide
```

`analytics.py` prints five sections to the terminal:

```
=== Top 10 Job Categories ===
  42  Software Development
  18  Customer Service
  15  Marketing
  ...

=== Top 15 Skills / Tags ===
  61  python
  44  sql
  30  aws
  ...

=== Jobs Posted in the Last 7 Days ===
2026-06-15  Backend Engineer @ Acme Remote
...

=== Companies With Most Open Listings ===
   7  Acme Remote
   5  Globex
...

=== Job Type Breakdown ===
  80  full_time
  12  contract
   8  unspecified
```

## What I'd add next

- Schedule it to run daily with cron (or Task Scheduler on Windows) so the
  database stays current
- Rebuild it as an Airflow DAG to handle retries and dependencies properly
- Swap SQLite for BigQuery so the data can grow past a local file
- Add a small Streamlit dashboard on top of the SQLite data instead of
  printing to the terminal
