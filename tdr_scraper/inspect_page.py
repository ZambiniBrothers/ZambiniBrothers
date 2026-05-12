#!/usr/bin/env python3
"""
Inspect TDR page to find wait time selector.
"""

import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def inspect_page():
    """Fetch and analyze the TDR page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = "https://www.tokyodisneyresort.jp/tdl/attraction/detail/189/"
        logger.info(f"Navigating to {url}")

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Get the page content
            html = await page.content()

            # Save HTML to file for inspection
            with open("/tmp/tdr_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            logger.info("HTML saved to /tmp/tdr_page.html")

            # Try to find elements containing "モンスターズ・インク" and numbers
            logger.info("\n=== Searching for relevant elements ===\n")

            # Look for text content
            all_text = await page.text_content()

            # Find sections with "モンスターズ・インク"
            if "モンスターズ・インク" in all_text:
                logger.info("Found 'モンスターズ・インク' in page")

            # Try various selectors
            selectors_to_try = [
                "span:has-text('分')",
                "div[class*='wait']",
                "div[class*='status']",
                "span[class*='time']",
                "p:has-text('分')",
                "[data-ride]",
                "[data-attraction]",
                ".attraction-status",
                ".wait-time",
                "div[class*='attraction-info']",
            ]

            logger.info("Trying various selectors:\n")
            for selector in selectors_to_try:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logger.info(f"✓ {selector}: Found {len(elements)} elements")
                        for i, elem in enumerate(elements[:3]):  # Show first 3
                            text = await elem.text_content()
                            class_attr = await elem.get_attribute("class")
                            id_attr = await elem.get_attribute("id")
                            logger.info(f"  [{i}] Text: {text[:100]}, class: {class_attr}, id: {id_attr}")
                except Exception as e:
                    logger.debug(f"✗ {selector}: {e}")

            # Look for elements containing "分"
            logger.info("\n=== Elements containing '分' ===\n")
            elements_with_fun = await page.query_selector_all("*:has-text('分')")
            logger.info(f"Found {len(elements_with_fun)} elements containing '分'")

            # Look for numbers followed by "分"
            logger.info("\n=== Detailed inspection ===\n")
            script = """
            () => {
                const results = [];
                document.querySelectorAll('*').forEach(elem => {
                    const text = elem.textContent.trim();
                    // Look for pattern like "XX分"
                    if (/\\d+\\s*分/.test(text) && text.length < 50) {
                        results.push({
                            tag: elem.tagName,
                            text: text,
                            class: elem.className,
                            id: elem.id,
                            parent: elem.parentElement ? elem.parentElement.tagName + '.' + elem.parentElement.className : 'none'
                        });
                    }
                });
                return results;
            }
            """

            results = await page.evaluate(script)
            logger.info(f"Found {len(results)} elements with wait time pattern:")
            for i, result in enumerate(results[:10]):
                logger.info(f"  [{i}] {result['tag']}.{result['class']} id={result['id']}")
                logger.info(f"      Text: {result['text']}")
                logger.info(f"      Parent: {result['parent']}\n")

        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_page())
