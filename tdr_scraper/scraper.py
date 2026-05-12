#!/usr/bin/env python3
"""
TDR Wait Time Scraper for Monsters, Inc. Ride & Go Seek!
Periodically fetches wait time data and calculates estimated queue line.
"""

import asyncio
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from playwright.async_api import async_playwright, Browser, Page

from config import CONFIG
from calculator import QueueCalculator
from utils import setup_logging, format_timestamp

logger = logging.getLogger(__name__)


class TDRScraper:
    """Scraper for Tokyo Disney Resort wait times."""

    RIDE_NAME = "モンスターズ・インク\"ライド＆ゴーシーク！\""
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.calculator = QueueCalculator()
        self.csv_path = Path(CONFIG["output_csv"])
        self._init_csv()

    def _init_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Wait Time (min)", "Estimated Queue"])
            logger.info(f"Created new CSV file: {self.csv_path}")

    async def init_browser(self) -> None:
        """Initialize Playwright browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        logger.info("Browser initialized")

    async def close_browser(self) -> None:
        """Close Playwright browser."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

    async def fetch_wait_time(self) -> Optional[int]:
        """
        Fetch wait time from TDR site.
        Returns wait time in minutes, or None if fetch fails.
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                page = await self.browser.new_page()
                await self._set_page_config(page)

                logger.info(f"Fetching wait time (Attempt {attempt + 1}/{self.MAX_RETRIES})")
                await page.goto(
                    CONFIG["tdr_url"],
                    wait_until="domcontentloaded",
                    timeout=CONFIG["page_timeout"],
                )

                wait_time = await self._extract_wait_time(page)
                await page.close()

                if wait_time is not None:
                    logger.info(f"Successfully fetched wait time: {wait_time} minutes")
                    return wait_time

                logger.warning(f"Wait time extraction failed on attempt {attempt + 1}")

            except Exception as e:
                logger.error(f"Error during fetch (attempt {attempt + 1}): {e}")
                await page.close()

            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(self.RETRY_DELAY)

        logger.error("All retry attempts failed")
        return None

    async def _set_page_config(self, page: Page) -> None:
        """Configure page headers and settings."""
        await page.set_extra_http_headers({
            "User-Agent": CONFIG["user_agent"],
        })

    async def _extract_wait_time(self, page: Page) -> Optional[int]:
        """
        Extract wait time from page using multiple strategies for resilience.
        """
        selectors = CONFIG["wait_time_selectors"]

        for selector_name, selector in selectors.items():
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        minutes = self._parse_wait_time(text)
                        if minutes is not None:
                            logger.info(f"Extracted via {selector_name}: {minutes} min")
                            return minutes
            except Exception as e:
                logger.debug(f"Selector '{selector_name}' failed: {e}")

        logger.warning("Could not find wait time using any selector strategy")
        return None

    def _parse_wait_time(self, text: str) -> Optional[int]:
        """
        Parse wait time from text.
        Handles formats like "45分", "45 minutes", "45" etc.
        """
        import re

        text = text.strip()

        patterns = [
            r"(\d+)\s*分",  # Japanese format: "45分"
            r"(\d+)\s*(?:min|minute)",  # English format: "45 minutes"
            r"(\d+)(?:\s+.*)?$",  # Just number: "45"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue

        logger.debug(f"Could not parse wait time from: '{text}'")
        return None

    def log_data(self, wait_time: int) -> None:
        """Log wait time and calculated queue size to CSV."""
        timestamp = format_timestamp()
        estimated_queue = self.calculator.calculate_queue(wait_time)

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, wait_time, estimated_queue])

        logger.info(f"Logged: {timestamp}, Wait: {wait_time}min, Queue: {estimated_queue} people")

    async def run_once(self) -> None:
        """Execute a single fetch-calculate-log cycle."""
        try:
            wait_time = await self.fetch_wait_time()
            if wait_time is not None:
                self.log_data(wait_time)
            else:
                logger.warning("Failed to fetch wait time this cycle")
        except Exception as e:
            logger.error(f"Unexpected error in run_once: {e}")

    async def run_loop(self, interval_seconds: int = 300) -> None:
        """
        Run the scraper in a continuous loop.

        Args:
            interval_seconds: Interval between scrapes (default: 300 = 5 minutes)
        """
        logger.info(f"Starting scraper loop with {interval_seconds}s interval")
        try:
            while True:
                await self.run_once()
                logger.info(f"Waiting {interval_seconds}s until next fetch...")
                await asyncio.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Scraper interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in loop: {e}")
        finally:
            await self.close_browser()


async def main():
    """Main entry point."""
    setup_logging()
    logger.info("=" * 60)
    logger.info("TDR Wait Time Scraper Started")
    logger.info("=" * 60)

    scraper = TDRScraper(headless=True)
    await scraper.init_browser()

    try:
        await scraper.run_loop(interval_seconds=CONFIG["interval_seconds"])
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await scraper.close_browser()


if __name__ == "__main__":
    asyncio.run(main())
