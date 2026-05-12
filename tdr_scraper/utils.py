"""
Utility functions for TDR Scraper.
"""

import logging
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_file: str = "tdr_scraper.log",
    level: int = logging.INFO,
) -> None:
    """
    Configure logging for the scraper.

    Args:
        log_file: Path to log file
        level: Logging level
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # File handler
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def format_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO format timestamp (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_hour() -> int:
    """Get current hour (0-23)."""
    return datetime.now().hour


def is_park_open(
    opening_hour: int = 8,
    closing_hour: int = 22,
) -> bool:
    """
    Check if Tokyo Disney Resort is likely open.

    Args:
        opening_hour: Park opening hour (default: 8 AM)
        closing_hour: Park closing hour (default: 10 PM)

    Returns:
        True if current time is within park hours
    """
    current_hour = get_current_hour()
    return opening_hour <= current_hour < closing_hour
