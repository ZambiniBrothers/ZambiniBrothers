"""TDR Wait Time Scraper Package."""

__version__ = "1.0.0"
__author__ = "TDR Analysis Team"

from .scraper import TDRScraper
from .calculator import QueueCalculator
from .config import CONFIG

__all__ = ["TDRScraper", "QueueCalculator", "CONFIG"]
