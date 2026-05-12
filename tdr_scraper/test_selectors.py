#!/usr/bin/env python3
"""
Test script to validate wait time selectors.
This script helps identify the correct selector for the TDR attraction page.
"""

import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_page_content():
    """Fetch the TDR attraction page and analyze its content."""

    url = "https://www.tokyodisneyresort.jp/tdl/attraction/detail/189/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser for debugging
        page = await browser.new_page()

        # Set user agent
        await page.set_extra_http_headers({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        })

        logger.info(f"Navigating to {url}")
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            logger.info("Page loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load page: {e}")
            await browser.close()
            return

        # Save HTML for inspection
        html = await page.content()
        html_file = Path("/tmp/tdr_attraction_page.html")
        html_file.write_text(html, encoding='utf-8')
        logger.info(f"HTML saved to {html_file}")

        # Try to find wait time elements
        logger.info("\n" + "="*80)
        logger.info("SEARCHING FOR WAIT TIME ELEMENTS")
        logger.info("="*80)

        # Test various selectors
        selectors_to_test = [
            ("All spans", "span"),
            ("All divs with 'wait'", "div[class*='wait']"),
            ("Spans with numbers", "span:contains('分')"),
            ("By data attributes", "[data-wait], [data-minutes], [data-waittime]"),
            ("Wait info box", "div[class*='waitInfo'], div[class*='wait-info']"),
            ("Attraction status", "[class*='attraction-status']"),
        ]

        for selector_name, selector in selectors_to_test:
            try:
                elements = await page.query_selector_all(selector)
                logger.info(f"\n[{selector_name}] Selector: {selector}")
                logger.info(f"  Found {len(elements)} element(s)")

                for i, element in enumerate(elements[:5]):  # Show first 5
                    text = await element.text_content()
                    text_preview = text[:100].replace('\n', ' ') if text else ""
                    logger.info(f"  [{i}] Text: {text_preview}")

                    # Get element tag and classes
                    tag = await element.evaluate("e => e.tagName")
                    class_attr = await element.evaluate("e => e.className")
                    logger.info(f"      Tag: {tag}, Classes: {class_attr}")
            except Exception as e:
                logger.debug(f"  Error testing selector: {e}")

        # Look for "分" (minutes) specifically
        logger.info("\n" + "="*80)
        logger.info("SEARCHING FOR '分' (MINUTES) KEYWORD")
        logger.info("="*80)

        page_text = await page.text_content()
        lines = [line.strip() for line in page_text.split('\n')
                 if '分' in line and any(c.isdigit() for c in line)]

        logger.info(f"Found {len(lines)} lines containing '分' with numbers:")
        for i, line in enumerate(lines[:20]):
            logger.info(f"  [{i}] {line[:150]}")

        # Try to get all text nodes around wait times
        logger.info("\n" + "="*80)
        logger.info("ANALYZING WAIT TIME ELEMENTS")
        logger.info("="*80)

        # Look for specific patterns
        try:
            # Pattern 1: Direct search for "45分" or similar
            all_spans = await page.query_selector_all("span")
            wait_time_candidates = []

            for span in all_spans:
                text = await span.text_content()
                if text and any(c.isdigit() for c in text) and '分' in text:
                    wait_time_candidates.append(text.strip())

            if wait_time_candidates:
                logger.info(f"\nWait time candidates found: {len(wait_time_candidates)}")
                for i, candidate in enumerate(wait_time_candidates[:10]):
                    logger.info(f"  [{i}] '{candidate}'")
        except Exception as e:
            logger.error(f"Error analyzing elements: {e}")

        logger.info("\n" + "="*80)
        logger.info("PAGE ANALYSIS COMPLETE")
        logger.info("="*80)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_page_content())
