#!/usr/bin/env python3
"""
Tokyo Disneyland - Monsters, Inc. Ride & Go Seek! Wait Time Scraper
東京ディズニーランド「モンスターズ・インク『ライド＆ゴーシーク！』」待ち時間自動取得エージェント

Periodically fetches wait time data and calculates estimated queue line.
5分ごとに待ち時間を自動取得し、推定Qライン人数を計算・記録します。

Vehicle Specifications for Queue Calculation:
- Dispatch Interval: 30 seconds
- Capacity per Dispatch: 12 people (6 per car × 2 cars connected)
- People per Minute: 24 people (12 × 2 dispatches/min)
- Calculation: Wait Time (minutes) × 24 = Estimated Queue People
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
    """
    Scraper for Tokyo Disneyland's Monsters, Inc. Ride & Go Seek!
    東京ディズニーランド「モンスターズ・インク『ライド＆ゴーシーク！』」用スクレーパー
    """

    # Target Attraction
    LOCATION = "Tokyo Disneyland (東京ディズニーランド)"
    RIDE_NAME = "Monsters, Inc. Ride & Go Seek!"
    RIDE_NAME_JP = "モンスターズ・インク『ライド＆ゴーシーク！』"
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
        Includes validation to ensure wait time is in 5-minute increments.
        Disney only displays wait times in 5-minute increments (5, 10, 15, 20, ...).
        """
        selectors = CONFIG["wait_time_selectors"]
        debug_attempts = []

        for selector_name, selector in selectors.items():
            try:
                # For the fallback strategy, we need special handling
                if selector == "JAVASCRIPT_EVAL":
                    logger.debug(f"Using fallback strategy: {selector_name}")
                    wait_time = await self._extract_via_fallback(page)
                    if wait_time is not None:
                        logger.info(f"✓ Successfully fetched wait time via {selector_name}: {wait_time} min")
                        return wait_time
                    debug_attempts.append(f"{selector_name}: no valid time found")
                    continue

                # Standard CSS selector query
                elements = await page.query_selector_all(selector)
                if not elements:
                    debug_attempts.append(f"{selector_name}: no elements found")
                    logger.debug(f"[{selector_name}] No elements found with selector")
                    continue

                # Check each found element
                for elem_index, element in enumerate(elements[:3]):  # Check first 3 matches
                    text = await element.text_content()
                    if not text:
                        continue

                    minutes = self._parse_wait_time(text)
                    if minutes is not None:
                        # Validate that minutes is a 5-minute increment
                        if self._is_valid_wait_time(minutes):
                            logger.info(f"✓ Successfully fetched wait time via {selector_name}: {minutes} min")
                            return minutes
                        else:
                            debug_attempts.append(
                                f"{selector_name}[{elem_index}]: invalid time {minutes}min "
                                f"(not 5-minute increment)"
                            )
                            logger.debug(
                                f"[{selector_name}] Element {elem_index} has invalid time: "
                                f"{minutes} min (not a 5-minute increment)"
                            )

            except Exception as e:
                logger.debug(f"[{selector_name}] Exception: {str(e)[:100]}")
                debug_attempts.append(f"{selector_name}: error - {str(e)[:50]}")

        # Log debugging information
        logger.warning("✗ Could not find valid wait time using any selector strategy")
        logger.debug(f"Attempts: {debug_attempts[:3]}")  # Show first 3 attempts for debugging
        return None

    async def _extract_via_fallback(self, page: Page) -> Optional[int]:
        """
        Fallback strategy: scan all elements for "XX分" pattern.
        This exhaustively searches for any element containing a valid wait time.
        """
        try:
            script = """
            () => {
                const results = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );

                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    // Match pattern like "45分" or "45 分"
                    const match = text.match(/\\b(\\d+)\\s*分\\b/);
                    if (match) {
                        const minutes = parseInt(match[1]);
                        // Prefer valid wait times (multiples of 5)
                        results.push({
                            text: text.substring(0, 50),
                            minutes: minutes,
                            isValid: minutes % 5 === 0 && minutes > 0,
                            parent: node.parentElement ? node.parentElement.className : 'unknown'
                        });
                    }
                }

                // Sort by validity and return top candidates
                results.sort((a, b) => {
                    if (a.isValid && !b.isValid) return -1;
                    if (!a.isValid && b.isValid) return 1;
                    return b.minutes - a.minutes;
                });

                return results.slice(0, 5);  // Return top 5 candidates
            }
            """
            candidates = await page.evaluate(script)
            logger.debug(f"Fallback found {len(candidates)} candidates: {candidates}")

            if candidates:
                # Prefer valid wait times first
                for candidate in candidates:
                    if candidate["isValid"]:
                        logger.debug(f"Fallback: Using valid time {candidate['minutes']} from '{candidate['text']}'")
                        return candidate["minutes"]

                # If no valid time found, still return the first one (it might be correct)
                logger.warning(f"Fallback: No valid 5-min increment found, using {candidates[0]['minutes']}")
                return candidates[0]["minutes"]

        except Exception as e:
            logger.debug(f"Fallback strategy failed: {e}")

        return None

    def _is_valid_wait_time(self, minutes: int) -> bool:
        """
        Validate that wait time is in valid 5-minute increments.
        Disney displays wait times in 5-minute increments only: 5, 10, 15, 20, ...

        Args:
            minutes: The wait time in minutes

        Returns:
            True if valid (multiple of 5), False otherwise
        """
        # Must be a positive multiple of 5
        # Valid: 5, 10, 15, 20, 25, 30, ...
        # Invalid: 1, 3, 7, 29, 43, etc.
        return minutes > 0 and minutes % 5 == 0

    def _parse_wait_time(self, text: str) -> Optional[int]:
        """
        Parse wait time from text.
        Handles formats like "45分", "45 minutes", "45" etc.
        """
        import re

        text = text.strip()

        # Remove extra whitespace/newlines
        text = ' '.join(text.split())

        patterns = [
            r"(\d+)\s*分",  # Japanese format: "45分"
            r"(\d+)\s*(?:min|minute)",  # English format: "45 minutes"
            r"(\d+)(?:\s+.*)?$",  # Just number: "45"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    parsed_value = int(match.group(1))
                    logger.debug(f"Parsed '{text}' -> {parsed_value}")
                    return parsed_value
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
    logger.info("=" * 70)
    logger.info("Tokyo Disneyland - Monsters, Inc. Ride & Go Seek! Wait Time Scraper")
    logger.info("東京ディズニーランド「モンスターズ・インク『ライド＆ゴーシーク！』」")
    logger.info("=" * 70)
    logger.info(f"Target: {TDRScraper.LOCATION} / {TDRScraper.RIDE_NAME_JP}")
    logger.info(f"Execution Interval: 5 minutes / 車両定員: 12名（6人乗り×2台）")

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
