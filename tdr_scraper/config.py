"""
Configuration for TDR Wait Time Scraper.
Tokyo Disneyland - Monsters, Inc. Ride & Go Seek (モンスターズ・インク「ライド＆ゴーシーク！」)

This configuration is specifically designed for:
- Location: 東京ディズニーランド (Tokyo Disneyland)
- Attraction: モンスターズ・インク「ライド＆ゴーシーク！」
- Vehicle Capacity: 12 people per dispatch (6 per car × 2 cars connected)
- Dispatch Interval: 30 seconds

All settings and calculations are calibrated for this specific attraction.
Do NOT use this scraper for other attractions without recalibrating parameters.
"""

CONFIG = {
    # ============================================================
    # TARGET ATTRACTION (対象アトラクション)
    # ============================================================
    # Location: Tokyo Disneyland (東京ディズニーランド)
    # Attraction: Monsters, Inc. Ride & Go Seek
    #           モンスターズ・インク「ライド＆ゴーシーク！」
    # ============================================================

    # Scraping settings
    "tdr_url": "https://www.tokyodisneyresort.jp/",
    "interval_seconds": 300,  # 5 minutes
    "page_timeout": 15000,  # 15 seconds in milliseconds

    # Wait time extraction selectors
    # Multiple selectors for resilience against HTML structure changes
    "wait_time_selectors": {
        # Strategy 1: Official TDR app/site - look for ride-specific wait time element
        "tdr_official_primary": "[data-ride='monsters-inc-ride-go-seek'] [class*='wait']",
        "tdr_official_secondary": "[aria-label*='モンスターズ'] [class*='time']",

        # Strategy 2: Common wait time patterns
        "wait_generic_class": ".wait-time, .waitTime, [class*='wait-time']",
        "wait_generic_span": "span[class*='wait']:not(.hidden)",

        # Strategy 3: Table/list based selectors (if data in table format)
        "table_cell_with_ride_name": "td:has-text('モンスターズ・インク') ~ td[class*='wait']",
        "table_row_wait_column": "tr:has-text('モンスターズ・インク') td:nth-child(3)",

        # Strategy 4: Fallback - API response or data attributes
        "data_attribute": "[data-waittime], [data-wait-minutes]",
    },

    # Browser settings
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
    "headless": True,

    # Output
    "output_csv": "tdr_analysis_log.csv",

    # Queue calculation parameters
    "dispatch_seconds": 30,
    "cars_per_dispatch": 2,
    "capacity_per_car": 6,
    "people_per_minute": 24,  # (capacity_per_car * cars_per_dispatch) / (dispatch_seconds / 60)
}


def update_selectors(new_selectors: dict) -> None:
    """
    Update wait time selectors when TDR website changes.
    Call this function to add new selectors as needed.

    Example:
        update_selectors({
            "new_strategy": "div.new-wait-element",
        })
    """
    CONFIG["wait_time_selectors"].update(new_selectors)
    print(f"Selectors updated. Total strategies: {len(CONFIG['wait_time_selectors'])}")
