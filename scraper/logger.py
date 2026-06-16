import logging
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

# matches the format: 2024-01-15 10:32:44 | INFO | extract | message
_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name):
    """Return a logger that writes to both console and logs/pipeline.log."""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # get_logger gets called from every module, don't stack handlers on re-import
    if logger.handlers:
        return logger

    formatter = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger
