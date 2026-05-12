#!/usr/bin/env python3
"""
TDR Wait Time Dashboard
Tokyo Disneyland - Monsters, Inc. Ride & Go Seek! - Wait Time Visualization Dashboard
東京ディズニーランド「モンスターズ・インク『ライド＆ゴーシーク！』」待ち時間ダッシュボード

Displays real-time wait time trends from tdr_analysis_log.csv with auto-refresh capability.
CSVデータから待ち時間推移をリアルタイム表示し、5分ごとに自動更新します。
"""

import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from flask import Flask, render_template, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
CONFIG = {
    "csv_file": "tdr_analysis_log.csv",
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False,
}

# Data cache
_cache = {
    "last_read": None,
    "data": None,
}


def read_csv_data() -> List[Dict[str, any]]:
    """
    Read CSV file and return parsed data.
    Returns list of dicts with keys: timestamp, wait_time, estimated_queue
    """
    csv_path = Path(CONFIG["csv_file"])

    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return []

    try:
        data = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    data.append({
                        "timestamp": row["Timestamp"],
                        "wait_time": int(row["Wait Time (min)"]),
                        "estimated_queue": int(row["Estimated Queue"]),
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping malformed row: {row} - {e}")
                    continue

        logger.info(f"Read {len(data)} records from CSV")
        return data

    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return []


def filter_last_hour(data: List[Dict]) -> List[Dict]:
    """
    Filter data to only include records from the past 1 hour.
    """
    if not data:
        return []

    try:
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        filtered = []
        for record in data:
            try:
                record_time = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")
                if record_time >= one_hour_ago:
                    filtered.append(record)
            except ValueError as e:
                logger.warning(f"Invalid timestamp format: {record['timestamp']} - {e}")
                continue

        return sorted(filtered, key=lambda x: x["timestamp"])

    except Exception as e:
        logger.error(f"Error filtering data: {e}")
        return data


def get_latest_record(data: List[Dict]) -> Optional[Dict]:
    """Get the most recent data record."""
    if not data:
        return None
    return data[-1]


def get_statistics(data: List[Dict]) -> Dict:
    """Calculate statistics from the data."""
    if not data:
        return {
            "avg_wait_time": 0,
            "max_wait_time": 0,
            "min_wait_time": 0,
            "avg_queue": 0,
            "max_queue": 0,
            "min_queue": 0,
        }

    wait_times = [r["wait_time"] for r in data]
    queues = [r["estimated_queue"] for r in data]

    return {
        "avg_wait_time": round(sum(wait_times) / len(wait_times), 1),
        "max_wait_time": max(wait_times),
        "min_wait_time": min(wait_times),
        "avg_queue": round(sum(queues) / len(queues), 0),
        "max_queue": max(queues),
        "min_queue": min(queues),
    }


@app.route("/")
def index():
    """Render the dashboard HTML."""
    return render_template("index.html")


@app.route("/api/data")
def get_data():
    """
    API endpoint to fetch dashboard data (JSON).
    Returns: {
        "success": bool,
        "data": List[{timestamp, wait_time, estimated_queue}],
        "latest": {timestamp, wait_time, estimated_queue},
        "stats": {...},
        "last_update": datetime,
        "error": str (if success=False)
    }
    """
    try:
        # Read CSV
        all_data = read_csv_data()

        if not all_data:
            return jsonify({
                "success": False,
                "data": [],
                "latest": None,
                "stats": {},
                "last_update": None,
                "error": "No data available. CSV file is empty or not found.",
            })

        # Filter to last hour
        filtered_data = filter_last_hour(all_data)

        # Get latest record from all data
        latest = get_latest_record(all_data)

        # Calculate statistics from filtered data
        stats = get_statistics(filtered_data)

        return jsonify({
            "success": True,
            "data": filtered_data,
            "latest": latest,
            "stats": stats,
            "last_update": datetime.now().isoformat(),
            "error": None,
        })

    except Exception as e:
        logger.error(f"Error in /api/data: {e}")
        return jsonify({
            "success": False,
            "data": [],
            "latest": None,
            "stats": {},
            "last_update": None,
            "error": f"Server error: {str(e)}",
        }), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


def main():
    """Start the Flask development server."""
    logger.info("=" * 70)
    logger.info("TDR Wait Time Dashboard")
    logger.info("Tokyo Disneyland - Monsters, Inc. Ride & Go Seek!")
    logger.info("東京ディズニーランド「モンスターズ・インク『ライド＆ゴーシーク！』」")
    logger.info("=" * 70)
    logger.info(f"Starting dashboard on http://localhost:{CONFIG['port']}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 70)

    app.run(
        host=CONFIG["host"],
        port=CONFIG["port"],
        debug=CONFIG["debug"],
    )


if __name__ == "__main__":
    main()
