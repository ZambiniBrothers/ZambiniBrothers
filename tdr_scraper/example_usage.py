#!/usr/bin/env python3
"""
Example usage of TDR Scraper and Calculator.
This script demonstrates how to use the modules without running the full scraper.
"""

import asyncio
from calculator import QueueCalculator
from config import CONFIG


def example_calculator():
    """Example: Calculate estimated queue line from wait times."""
    print("=" * 60)
    print("Example 1: Queue Calculation")
    print("=" * 60)

    calculator = QueueCalculator()

    test_wait_times = [30, 45, 60, 90, 120]

    for wait_time in test_wait_times:
        estimated_queue = calculator.calculate_queue(wait_time)
        details = calculator.validate_calculation(wait_time, estimated_queue)

        print(f"\n待ち時間: {wait_time}分")
        print(f"  → 推定Qライン人数: {estimated_queue}人")
        print(f"  → 計算根拠:")
        print(f"     - 1回の乗車人数: {details['capacity_per_dispatch']}人")
        print(f"     - 1分間のディスパッチ回数: {details['dispatch_frequency_per_min']:.1f}回")
        print(f"     - 1分間のキャリー人数: {details['people_per_minute']:.0f}人")

    print("\n")


def example_config():
    """Example: Display current configuration."""
    print("=" * 60)
    print("Example 2: Current Configuration")
    print("=" * 60)

    print(f"\n取得対象サイト: {CONFIG['tdr_url']}")
    print(f"実行間隔: {CONFIG['interval_seconds']}秒 ({CONFIG['interval_seconds'] // 60}分)")
    print(f"ページタイムアウト: {CONFIG['page_timeout']}ms")
    print(f"出力CSV: {CONFIG['output_csv']}")
    print(f"1分間のキャリー人数: {CONFIG['people_per_minute']}人")

    print(f"\nセレクタ戦略数: {len(CONFIG['wait_time_selectors'])}")
    for name, selector in CONFIG["wait_time_selectors"].items():
        print(f"  - {name}")
        print(f"    セレクタ: {selector}")

    print("\n")


def example_update_config():
    """Example: How to update selectors if website changes."""
    print("=" * 60)
    print("Example 3: Updating Selectors (for Website Changes)")
    print("=" * 60)

    from config import update_selectors

    print("\n現在のセレクタ数:", len(CONFIG["wait_time_selectors"]))

    print("\n新しいセレクタを追加中...")
    update_selectors({
        "tdr_new_structure_v2": "div[data-attraction='monsters-inc'] .wait-time-value",
        "tdr_new_structure_v3": "[role='status'] span[class*='wait']",
    })

    print("更新後のセレクタ数:", len(CONFIG["wait_time_selectors"]))
    print("\n")


def example_manual_logging():
    """Example: Manually log data without scraping (for testing)."""
    print("=" * 60)
    print("Example 4: Manual Data Logging (Test Only)")
    print("=" * 60)

    import csv
    from pathlib import Path
    from utils import format_timestamp
    from calculator import QueueCalculator

    csv_file = "example_log.csv"
    csv_path = Path(csv_file)

    if not csv_path.exists():
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Wait Time (min)", "Estimated Queue"])
        print(f"Created new CSV file: {csv_file}")

    calculator = QueueCalculator()

    print("\nサンプルデータを記録中...")
    test_data = [
        (35, "10:00朝の入園時間"),
        (60, "10:30通常営業時間"),
        (85, "13:00昼間のピーク時"),
        (95, "16:00午後のピーク時"),
        (70, "19:00夜間営業時間"),
    ]

    for wait_time, description in test_data:
        timestamp = format_timestamp()
        estimated_queue = calculator.calculate_queue(wait_time)
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([f"{timestamp} ({description})", wait_time, estimated_queue])
        print(f"  ✓ {timestamp}: {wait_time}分 → {estimated_queue}人")

    print(f"\nデータは {csv_file} に保存されました。")
    print("(本番環境では自動的に tdr_analysis_log.csv に保存されます)")
    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  TDR Wait Time Scraper - Usage Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    try:
        example_calculator()
        example_config()
        example_update_config()
        example_manual_logging()

        print("=" * 60)
        print("すべての例が完了しました！")
        print("=" * 60)
        print("\n実際にスクレーパーを実行するには以下を実行してください:")
        print("  python scraper.py")
        print("\nスクリプトを停止するには Ctrl + C を押してください")
        print("\n")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()
