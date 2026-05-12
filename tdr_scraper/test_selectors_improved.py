#!/usr/bin/env python3
"""
Improved selector testing script for TDR Wait Time Scraper.
Tests selectors and provides detailed feedback on what's being extracted.

This script will try to run with Playwright if available, otherwise provides guidance.
"""

import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_with_playwright():
    """Test using Playwright (requires proper installation)."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright is not installed properly.")
        logger.error("Run: playwright install")
        return False

    from config import CONFIG

    url = CONFIG["tdr_url"]
    user_agent = CONFIG["user_agent"]

    logger.info(f"Testing URL: {url}")
    logger.info(f"Using User-Agent: {user_agent[:60]}...")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.set_extra_http_headers({"User-Agent": user_agent})

            logger.info("\nLoading page...")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            logger.info("✓ Page loaded")

            # Test each selector
            selectors = CONFIG["wait_time_selectors"]
            valid_selectors = []

            logger.info("\n" + "=" * 80)
            logger.info("TESTING SELECTORS")
            logger.info("=" * 80 + "\n")

            for selector_name, selector in selectors.items():
                if selector == "JAVASCRIPT_EVAL":
                    logger.info(f"[{selector_name}] (Fallback JavaScript evaluation)")
                    continue

                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logger.info(f"✓ [{selector_name}] Found {len(elements)} elements")

                        # Check each element for valid wait time
                        for i, elem in enumerate(elements[:2]):
                            text = await elem.text_content()
                            if text:
                                import re
                                match = re.search(r"(\d+)\s*分", text)
                                if match:
                                    minutes = int(match.group(1))
                                    is_valid = minutes > 0 and minutes % 5 == 0
                                    status = "✓ VALID" if is_valid else "✗ INVALID"
                                    logger.info(f"  Element {i}: {minutes}min {status} - {text[:60]}")
                                    if is_valid:
                                        valid_selectors.append(selector_name)
                                        break
                    else:
                        logger.info(f"✗ [{selector_name}] No elements found")

                except Exception as e:
                    logger.debug(f"✗ [{selector_name}] Error: {e}")

            logger.info("\n" + "=" * 80)
            logger.info("RESULTS")
            logger.info("=" * 80)

            if valid_selectors:
                logger.info(f"\n✓ Found {len(valid_selectors)} working selector(s):")
                for selector in valid_selectors:
                    logger.info(f"  - {selector}")
                logger.info("\n✓ Scraper should be able to fetch wait time")
            else:
                logger.warning("\n✗ No working selectors found")
                logger.warning("The page structure may have changed")
                logger.warning("Next steps:")
                logger.warning("1. Check if page loads correctly (use headless=False)")
                logger.warning("2. Inspect page HTML manually")
                logger.warning("3. Update selectors in config.py based on actual HTML")

            await browser.close()
            return len(valid_selectors) > 0

    except Exception as e:
        logger.error(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("TDR WAIT TIME SCRAPER - SELECTOR TEST")
    logger.info("=" * 80 + "\n")

    try:
        success = await test_with_playwright()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
