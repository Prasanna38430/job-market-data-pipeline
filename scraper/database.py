import os
import sys
import getpass
from urllib.parse import quote_plus

from scraper.logger import get_logger

log = get_logger("database")

DEFAULT_PORTS = {"postgres": "5432", "mysql": "3306"}

# sqlalchemy needs a driver in the url. these are the ones in requirements.txt
DRIVERS = {
    "postgres": "postgresql+psycopg2",
    "mysql": "mysql+pymysql",
}


def export_to_database(df, engine_name):
    """Mirror the full clean table to postgres or mysql.

    Credentials come from a .env file or environment variables. If something is
    missing and we're in a real terminal, we ask for it (password stays hidden).
    """
    if df.empty:
        log.info("empty dataframe, skipping database export")
        return

    try:
        from sqlalchemy import create_engine
    except ImportError:
        log.error("sqlalchemy not installed - run: pip install sqlalchemy")
        return

    config = _get_config(engine_name)
    if config is None:
        log.error("missing database credentials, skipping database export")
        return

    url = _build_url(engine_name, config)
    try:
        engine = create_engine(url)
        # sqlite already deduped the data, so we just replace the snapshot each run
        df.to_sql(config["table"], engine, if_exists="replace", index=False)
        engine.dispose()
        log.info(f"wrote {len(df)} rows to {engine_name} table '{config['table']}'")
    except Exception as e:
        # never log the url itself, it has the password in it
        log.error(f"could not write to {engine_name}: {e}")


def _get_config(engine_name):
    _load_dotenv()

    config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "name": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "table": os.getenv("DB_TABLE", "jobs"),
    }

    required = ["host", "name", "user", "password"]
    missing = [k for k in required if not config[k]]

    if missing:
        if not sys.stdin.isatty():
            # unattended run (cron/airflow) - can't prompt, so bail with a clear message
            log.error(f"db settings missing and no terminal to ask for them: {missing}")
            return None
        try:
            config = _prompt_config(engine_name, config)
        except (EOFError, KeyboardInterrupt):
            # no input available, or the user bailed out of the prompt
            log.error("no db credentials entered, skipping database export")
            return None

    if not config["port"]:
        config["port"] = DEFAULT_PORTS[engine_name]

    return config


def _prompt_config(engine_name, current):
    print(f"\nenter {engine_name} connection details (press enter to keep the default):")
    current["host"] = _ask("host", current["host"] or "localhost")
    current["port"] = _ask("port", current["port"] or DEFAULT_PORTS[engine_name])
    current["name"] = _ask("database name", current["name"])
    current["user"] = _ask("user", current["user"])
    if not current["password"]:
        current["password"] = getpass.getpass("  password: ")
    return current


def _ask(label, default):
    shown = f" [{default}]" if default else ""
    answer = input(f"  {label}{shown}: ").strip()
    return answer or default


def _build_url(engine_name, config):
    driver = DRIVERS[engine_name]
    # quote the password so special chars like @ or / don't break the url
    pwd = quote_plus(config["password"] or "")
    user = config["user"]
    return f"{driver}://{user}:{pwd}@{config['host']}:{config['port']}/{config['name']}"


def _load_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        # dotenv is optional, plain env vars still work without it
        pass
