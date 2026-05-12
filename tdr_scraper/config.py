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
    # Updated to correct attraction detail page URL
    "tdr_url": "https://www.tokyodisneyresort.jp/tdl/attraction/detail/189/",
    "interval_seconds": 300,  # 5 minutes
    "page_timeout": 15000,  # 15 seconds in milliseconds

    # Wait time extraction selectors
    # Multiple selectors for resilience against HTML structure changes
    # NOTE: These selectors are tried in order until one returns a valid 5-minute increment
    "wait_time_selectors": {
        # Strategy 1: TDR Official Detail Page - header/info section for Monsters Inc
        # Look for the main wait time display in the attraction header
        "tdr_detail_header_wait": "div[class*='attraction-header'] span[class*='wait-time'], div[class*='info'] span[class*='time']",
        "tdr_monsters_inc_wait": "div[class*='monsters'] span[class*='wait'], span[data-attraction='monsters-inc']",

        # Strategy 2: Common TDR attraction info patterns
        # TDR typically displays wait time in a dedicated info box with "待ち時間" or similar label
        "tdr_attraction_info_wait": "div[class*='attraction-info'] span, div[class*='attract-status'] span",
        "tdr_wait_time_box": "div.wait-time-box span, div[class*='waitTimeBox'] span, div[class*='wait_time'] span",

        # Strategy 3: Direct number + "分" pattern (works across most Japanese sites)
        # Looks for the first clear "N分" pattern that matches a 5-minute increment
        "japanese_minutes_main": "span[class*='number'] ~ span:contains('分'), span[class*='value']:contains('分')",
        "minutes_with_number": "span:contains('分') > span, span > span:contains('分')",

        # Strategy 4: Status/info displays on attraction detail pages
        "status_info_wait": "div[class*='status'] span, p[class*='wait'] span, li[class*='wait'] span",
        "info_panel_wait": "div[class*='info-panel'] span, section[class*='wait'] span, article[class*='wait'] span",

        # Strategy 5: Data attributes and ARIA labels
        "data_attribute_wait": "[data-waittime], [data-wait-minutes], [data-minutes], [aria-label*='分']",

        # Strategy 6: Fallback - generic patterns
        "generic_patterns": "span[class*='wait'], .wait-minutes, .minutes, .time-display",
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
