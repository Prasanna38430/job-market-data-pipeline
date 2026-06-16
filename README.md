# Job Market Data Pipeline

A small Python data pipeline that pulls remote job listings, cleans them up,
stores them in a database, and turns them into a quick read on the job market.

It runs the full path on its own: pull the data, clean it, save it, and report
on it. You can export the clean data as CSV, Parquet, or JSON, and optionally
push it straight into Postgres or MySQL.

## What you get

Every run produces:

- a **clean dataset** of job listings (CSV, Parquet, or JSON — your choice)
- a **SQLite database** that keeps growing across runs without duplicating jobs
- a **plain-English report** printed to the screen: top categories, most common
  skills, recent postings, top hiring companies, and job-type breakdown

You can see real output without running anything:

- [examples/sample_jobs_clean.csv](examples/sample_jobs_clean.csv) — a few rows of the cleaned data
- [examples/analytics_output.txt](examples/analytics_output.txt) — the full report from a real run

## Sample report

This is actual output, not made up:

```
=== Top 10 Job Categories ===
  10  Software Development
   5  Product Management
   4  All others
   3  Sales
   2  Data and Analytics

=== Top 15 Skills / Tags ===
  17  AI/ML
  13  REST
  12  react
  12  github
  11  backend

=== Job Type Breakdown ===
  21  full_time
   4  part_time
   3  freelance
   3  contract
```

## How it works

The pipeline runs in four steps:

1. **Extract** — pull job listings from the Remotive API and save the raw
   response so every run can be traced back.
2. **Transform** — clean the data with Pandas: rename fields, strip extra
   spaces, flatten the tags list, fix dates, and drop duplicates and
   incomplete rows.
3. **Load** — insert new jobs into SQLite. It checks what's already there and
   skips anything it has seen before, so re-running won't create duplicates.
4. **Report** — run a set of queries and print the results.

SQLite is the source of truth and handles the deduplication. The file exports
and the external database are just snapshots of that clean table.

## How to run

```bash
# 1. get the code
git clone <your-repo-url>
cd job-market-scraper

# 2. set up a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate        # on Windows
source .venv/bin/activate     # on mac/linux
pip install -r requirements.txt

# 3. run the full pipeline (fetches 100 jobs, saves a CSV by default)
python pipeline.py

# fetch a different number of jobs
python pipeline.py --limit 250

# 4. print the report
python analytics.py
```

### Choosing output formats

Use `--format` to pick one or more file formats (comma separated):

```bash
python pipeline.py --format csv              # default
python pipeline.py --format parquet
python pipeline.py --format csv,parquet,json
```

Files land in `data/processed/` as `jobs_clean.csv`, `jobs_clean.parquet`,
and so on.

### Saving to a database (Postgres or MySQL)

Use `--db` to also push the clean table to Postgres or MySQL:

```bash
python pipeline.py --db postgres
python pipeline.py --format parquet --db mysql
```

Credentials come from a `.env` file (copy `.env.example` to `.env` and fill it
in). If something is missing and you're running by hand, the pipeline asks for
it in the terminal — the password is typed hidden and never written to the log.
This keeps secrets out of the code and out of git, and still lets the pipeline
run unattended on a schedule.

## Tests

```bash
python -m pytest          # if you have pytest
python tests/test_transform.py   # or just run it directly
```

The tests cover the cleaning logic: deduplication, dropping incomplete rows,
date formatting, and tag flattening.

## Project structure

```
job-market-scraper/
├── scraper/
│   ├── logger.py      shared logging config (console + file)
│   ├── extract.py     calls the Remotive API, saves raw JSON
│   ├── transform.py   cleans and dedupes the data with Pandas
│   ├── load.py        incremental insert into SQLite, returns clean table
│   ├── export.py      writes the table to csv / parquet / json
│   └── database.py    pushes the table to Postgres or MySQL
├── analytics.py       runs the report queries and prints results
├── pipeline.py        runs extract -> transform -> load end to end
├── tests/             tests for the cleaning logic
├── examples/          sample output you can look at without running it
├── data/              raw responses, clean exports, and the SQLite db
├── logs/              pipeline.log
├── requirements.txt
├── .env.example       template for database credentials
└── README.md
```

## Tech stack

- Python 3
- Requests — HTTP calls
- Pandas — data cleaning
- SQLite — local storage and dedup
- PyArrow — Parquet export
- SQLAlchemy + python-dotenv — optional Postgres/MySQL export
- Logging — so every run leaves a trail

## What I'd add next

- Schedule it to run daily (cron, or Task Scheduler on Windows) so the database
  stays current
- Rebuild it as an Airflow DAG to handle retries and step dependencies
- Swap SQLite for BigQuery so the data can grow past a local file
- Add a small Streamlit dashboard instead of printing to the terminal

## License

MIT — see [LICENSE](LICENSE).
