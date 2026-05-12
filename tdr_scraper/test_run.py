#!/usr/bin/env python3
"""
Quick test script to verify the scraper works correctly.
Runs a single fetch-calculate-log cycle and displays results.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper import TDRScraper
from utils import setup_logging
import logging

logger = logging.getLogger(__name__)


async def test_scraper():
    """Run a single scraper test cycle."""
    setup_logging()

    logger.info("="*70)
    logger.info("TDR Wait Time Scraper - TEST RUN")
    logger.info("="*70)

    scraper = TDRScraper(headless=True)
    await scraper.init_browser()

    try:
        logger.info("\nAttempting to fetch wait time from:")
        logger.info("URL: https://www.tokyodisneyresort.jp/tdl/attraction/detail/189/")
        logger.info("\nRunning fetch cycle...\n")

        await scraper.run_once()

        # Read and display the CSV
        logger.info("\n" + "="*70)
        logger.info("RECENT CSV ENTRIES:")
        logger.info("="*70)

        csv_path = Path("tdr_analysis_log.csv")
        if csv_path.exists():
            with open(csv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Show header and last 5 entries
                for line in lines[-6:]:
                    logger.info(line.rstrip())

        logger.info("\n" + "="*70)
        logger.info("TEST COMPLETE")
        logger.info("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.close_browser()


if __name__ == "__main__":
    asyncio.run(test_scraper())
