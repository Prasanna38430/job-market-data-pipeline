import sqlite3
from collections import Counter

DB_PATH = "data/jobs.db"


def header(title):
    print(f"\n=== {title} ===")


def top_categories(conn):
    header("Top 10 Job Categories")
    rows = conn.execute(
        """
        SELECT category, COUNT(*) as job_count
        FROM jobs
        GROUP BY category
        ORDER BY job_count DESC
        LIMIT 10
        """
    ).fetchall()
    for category, count in rows:
        print(f"{count:>4}  {category}")


def top_tags(conn):
    header("Top 15 Skills / Tags")
    # tags are stored comma separated, so split and count in python
    counter = Counter()
    for (tags,) in conn.execute("SELECT tags FROM jobs WHERE tags IS NOT NULL"):
        for tag in tags.split(","):
            tag = tag.strip()
            if tag:
                counter[tag] += 1
    for tag, count in counter.most_common(15):
        print(f"{count:>4}  {tag}")


def recent_jobs(conn):
    header("Jobs Posted in the Last 7 Days")
    rows = conn.execute(
        """
        SELECT job_title, company_name, posted_date
        FROM jobs
        WHERE posted_date >= date('now', '-7 days')
        ORDER BY posted_date DESC
        """
    ).fetchall()
    if not rows:
        print("none")
    for title, company, posted in rows:
        print(f"{posted}  {title} @ {company}")


def top_companies(conn):
    header("Companies With Most Open Listings")
    rows = conn.execute(
        """
        SELECT company_name, COUNT(*) as openings
        FROM jobs
        GROUP BY company_name
        ORDER BY openings DESC
        LIMIT 10
        """
    ).fetchall()
    for company, openings in rows:
        print(f"{openings:>4}  {company}")


def job_type_breakdown(conn):
    header("Job Type Breakdown")
    rows = conn.execute(
        """
        SELECT job_type, COUNT(*) as count
        FROM jobs
        GROUP BY job_type
        ORDER BY count DESC
        """
    ).fetchall()
    for job_type, count in rows:
        print(f"{count:>4}  {job_type or 'unspecified'}")


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        top_categories(conn)
        top_tags(conn)
        recent_jobs(conn)
        top_companies(conn)
        job_type_breakdown(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
