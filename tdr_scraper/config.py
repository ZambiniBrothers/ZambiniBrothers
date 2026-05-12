"""
Configuration for TDR Wait Time Scraper.
Tokyo Disneyland - Monsters, Inc. Ride & Go Seek (モンスターズ・インク「ライド＆ゴーシーク！」)

This configuration is specifically designed for:
- Location: 東京ディズニーランド (Tokyo Disneyland)
- Attraction: モンスターズ・インク「ライド＆ゴーシーク！」
- Attraction ID: 189
- URL: https://www.tokyodisneyresort.jp/tdl/attraction/detail/189/
- Vehicle Capacity: 12 people per dispatch (6 per car × 2 cars connected)
- Dispatch Interval: 30 seconds

All settings and calculations are calibrated for this specific attraction.
Do NOT use this scraper for other attractions without recalibrating parameters.

WAIT TIME RULES (ディズニー待ち時間表記ルール):
- Disney displays wait times ONLY in 5-minute increments: 5, 10, 15, 20, 25, 30, ...
- Fractional minutes are truncated (not rounded)
- Examples:
  - 8 minutes actual = 5 minutes displayed (3 truncated)
  - 14 minutes actual = 10 minutes displayed (4 truncated)
  - 47 minutes actual = 45 minutes displayed (2 truncated)

CSV DATA ISSUE (既知の問題):
- Previous data showed 29, 27, 25, 43 minutes (invalid - not 5-minute increments)
- This indicates selectors were capturing wrong data (not actual wait times)
- Current selectors have been improved to validate 5-minute increments
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
    # All wait times must be multiples of 5 (5, 10, 15, 20, 25, 30, ...)
    "wait_time_selectors": {
        # ===== PRIMARY STRATEGIES (Most Likely) =====

        # Strategy 1: TDR Official Detail Page - Attraction Info Section
        # Most TDR detail pages have a dedicated info section with wait time
        # Typical pattern: <div class="attraction-info"><span>待ち時間</span><span>45分</span></div>
        "tdr_attraction_info_section": (
            "div[class*='attraction-info'] span[class*='wait'], "
            "div[class*='info-box'] span:contains('分'), "
            "div[class*='detail-info'] span:contains('分')"
        ),

        # Strategy 2: Header/Top Section Info Display
        # Wait time often displayed prominently near attraction title
        # Typical pattern in header/top area
        "tdr_header_wait_display": (
            "header span[class*='wait'], "
            "div[class*='header'] span:contains('分'), "
            "div[class*='top-info'] span:contains('分')"
        ),

        # Strategy 3: Semantic HTML Labels + Value Pattern
        # <strong>待ち時間</strong> followed by time value
        # This is very common in Japanese websites
        "tdr_label_value_pattern": (
            "strong:contains('待ち時間') ~ span:first-of-type, "
            "label:contains('待ち時間') ~ span, "
            "dt:contains('待ち時間') ~ dd span"
        ),

        # Strategy 4: Data Attributes (for JavaScript-based rendering)
        # React/Vue often store data in data-* attributes
        "tdr_data_attributes": (
            "[data-wait-time], [data-waittime], [data-minutes], "
            "[data-wait-minutes], [title*='分']"
        ),

        # ===== SECONDARY STRATEGIES (Common Patterns) =====

        # Strategy 5: Direct "分" containing spans
        # Simple pattern: any span containing "XX分"
        "japanese_minutes_span": (
            "span:contains('分'), "
            "div[class*='minutes'] span, "
            "p[class*='wait'] span"
        ),

        # Strategy 6: Status/Info Box Elements
        # Information displayed in boxes or panels
        "tdr_info_panel": (
            "div[class*='status'] span, "
            "div[class*='info-panel'] span, "
            "section[class*='info'] span"
        ),

        # Strategy 7: List Items (if displayed as list)
        # Some pages display attractions as lists with wait times
        "tdr_list_items": (
            "li span:contains('分'), "
            "tr td[class*='wait'] span, "
            "tr:contains('モンスターズ') td span"
        ),

        # Strategy 8: Specific number + unit patterns
        # <span class="number">45</span> <span class="unit">分</span>
        "tdr_number_unit_pattern": (
            "span[class*='number'] ~ span:contains('分'), "
            "span[class*='value'] ~ span:contains('分'), "
            "span[class*='time-value'] span"
        ),

        # ===== TERTIARY STRATEGIES (Fallback) =====

        # Strategy 9: Content-based search
        # Last resort: search page text for valid wait time patterns
        # This is handled via JavaScript evaluation
        "fallback_minutes": "JAVASCRIPT_EVAL",  # Special handling in scraper.py
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
