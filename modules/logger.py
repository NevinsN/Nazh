import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configures a professional logging pipeline with console and file output.
    """
    # 1. Define the log format (Time - Name - Level - Message)
    # SRE Note: Standardized formats allow tools like Datadog to parse logs automatically.
    log_format = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 2. Setup Console Handler (Standard Output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    # 3. Setup File Handler (Rotating)
    # This prevents the log file from growing until it crashes the server.
    file_handler = RotatingFileHandler(
        "nazh_engine.log", maxBytes=10**6, backupCount=3
    )
    file_handler.setFormatter(log_format)

    # 4. Configure Root Logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logging.info("LOGGING_INIT: Structured logging pipeline established.")

# 
