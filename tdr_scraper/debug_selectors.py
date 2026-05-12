#!/usr/bin/env python3
"""
Advanced selector debugging script.
Tests all selectors and shows detailed results about what's being extracted.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from config import CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def debug_selectors_with_playwright():
    """
    Debug selectors using Playwright.
    This requires Playwright to be properly installed.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright not installed. Install with: pip install playwright && playwright install")
        return

    url = CONFIG["tdr_url"]
    user_agent = CONFIG["user_agent"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_extra_http_headers({"User-Agent": user_agent})

        logger.info(f"\nLoading page: {url}")
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            logger.info("Page loaded successfully\n")
        except Exception as e:
            logger.error(f"Failed to load page: {e}")
            await browser.close()
            return

        # Test all selectors
        selectors = CONFIG["wait_time_selectors"]
        results: Dict[str, Any] = {}

        logger.info("=" * 80)
        logger.info("TESTING ALL SELECTORS")
        logger.info("=" * 80 + "\n")

        for selector_name, selector in selectors.items():
            logger.info(f"[{selector_name}]")
            logger.info(f"  Selector: {selector}")

            try:
                if selector_name == "fallback_minutes":
                    logger.info("  (Fallback strategy - special handling)")
                    continue

                elements = await page.query_selector_all(selector)
                logger.info(f"  Found {len(elements)} element(s)")

                found_valid_time = False
                for i, elem in enumerate(elements[:5]):  # Show first 5
                    text = await elem.text_content()
                    text_clean = " ".join(text.split())[:100] if text else ""
                    tag = await elem.evaluate("e => e.tagName")
                    class_attr = await elem.evaluate("e => e.className") or ""

                    logger.info(f"    [{i}] Tag: {tag}, Classes: {class_attr[:50]}")
                    logger.info(f"        Text: {text_clean}")

                    # Try to parse this text
                    import re
                    match = re.search(r"(\d+)\s*分", text)
                    if match:
                        parsed_min = int(match.group(1))
                        is_valid = parsed_min > 0 and parsed_min % 5 == 0
                        status = "✓ VALID" if is_valid else "✗ INVALID"
                        logger.info(f"        Parsed: {parsed_min}min {status}")
                        if is_valid:
                            found_valid_time = True

                results[selector_name] = {
                    "count": len(elements),
                    "found_valid": found_valid_time
                }

            except Exception as e:
                logger.info(f"  ERROR: {e}")
                results[selector_name] = {"count": 0, "error": str(e)}

            logger.info()

        # Fallback strategy detailed test
        logger.info("[fallback_minutes - DETAILED TEST]")
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
                    const match = text.match(/\\b(\\d+)\\s*分\\b/);
                    if (match) {
                        const minutes = parseInt(match[1]);
                        results.push({
                            text: text.substring(0, 100),
                            minutes: minutes,
                            isValid: minutes % 5 === 0 && minutes > 0,
                            parent: node.parentElement ? node.parentElement.className : 'unknown',
                            xpath: node.parentElement ? node.parentElement.tagName : 'unknown'
                        });
                    }
                }

                results.sort((a, b) => {
                    if (a.isValid && !b.isValid) return -1;
                    if (!a.isValid && b.isValid) return 1;
                    return b.minutes - a.minutes;
                });

                return results.slice(0, 10);
            }
            """
            candidates = await page.evaluate(script)
            logger.info(f"  Found {len(candidates)} candidates with '分' pattern:")
            for i, cand in enumerate(candidates):
                status = "✓" if cand["isValid"] else "✗"
                logger.info(f"    [{i}] {status} {cand['minutes']}min - {cand['text'][:60]}")
                logger.info(f"        Parent: {cand['xpath']}.{cand['parent'][:40]}")

            results["fallback_minutes"] = {"count": len(candidates), "candidates": candidates}

        except Exception as e:
            logger.error(f"  Fallback test failed: {e}")

        # Page content analysis
        logger.info("\n" + "=" * 80)
        logger.info("PAGE CONTENT ANALYSIS")
        logger.info("=" * 80 + "\n")

        page_text = await page.text_content()
        lines_with_minutes = [
            line.strip() for line in page_text.split('\n')
            if '分' in line and any(c.isdigit() for c in line)
        ]

        logger.info(f"Lines containing '分' with numbers: {len(lines_with_minutes)}")
        for i, line in enumerate(lines_with_minutes[:15]):
            logger.info(f"  [{i}] {line[:100]}")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80 + "\n")

        valid_selectors = [name for name, data in results.items() if data.get("found_valid")]
        if valid_selectors:
            logger.info(f"✓ Selectors that found valid wait time (5-min increments):")
            for name in valid_selectors:
                logger.info(f"  - {name}")
        else:
            logger.info("✗ No selectors found valid wait time (5-min increment)")
            logger.info("\nRecommendations:")
            logger.info("  1. Check the page manually (headless=False)")
            logger.info("  2. Look at the actual HTML structure")
            logger.info("  3. Update selectors based on real HTML")

        logger.info(f"\n\nDetailed results saved:")
        results_file = Path("/tmp/selector_debug_results.json")
        results_file.write_text(json.dumps(results, indent=2, default=str))
        logger.info(f"  {results_file}")

        await browser.close()


async def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("TDR WAIT TIME SELECTOR DEBUG UTILITY")
    logger.info("=" * 80)

    await debug_selectors_with_playwright()


if __name__ == "__main__":
    asyncio.run(main())
