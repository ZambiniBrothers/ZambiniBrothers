"""
Queue line estimation calculator for Monsters, Inc. attraction.
"""

from config import CONFIG


class QueueCalculator:
    """Calculate estimated queue line based on wait time."""

    def __init__(self):
        self.people_per_minute = CONFIG["people_per_minute"]

    def calculate_queue(self, wait_time_minutes: int) -> int:
        """
        Calculate estimated number of people in queue line.

        Calculation:
        - 1 dispatch: 30 seconds
        - 1 ride capacity: 12 people (6 per car × 2 cars)
        - 1 minute capacity: 24 people (12 people / 0.5 minutes)
        - Formula: wait_time_minutes × 24 = estimated_queue

        Args:
            wait_time_minutes: Wait time in minutes

        Returns:
            Estimated number of people in queue
        """
        estimated_queue = wait_time_minutes * self.people_per_minute
        return int(estimated_queue)

    def calculate_dispatch_capacity(self) -> int:
        """Get capacity per dispatch cycle."""
        return CONFIG["capacity_per_car"] * CONFIG["cars_per_dispatch"]

    def calculate_dispatch_frequency_per_minute(self) -> float:
        """Get number of dispatches per minute."""
        return 60 / CONFIG["dispatch_seconds"]

    def validate_calculation(self, wait_time: int, estimated_queue: int) -> dict:
        """
        Validate the calculation and return breakdown details.

        Returns:
            Dictionary with calculation breakdown
        """
        dispatch_capacity = self.calculate_dispatch_capacity()
        dispatch_freq = self.calculate_dispatch_frequency_per_minute()
        calculated_capacity_per_min = dispatch_capacity * dispatch_freq

        return {
            "wait_time_minutes": wait_time,
            "estimated_queue": estimated_queue,
            "capacity_per_dispatch": dispatch_capacity,
            "dispatch_frequency_per_min": dispatch_freq,
            "people_per_minute": calculated_capacity_per_min,
            "calculation_valid": abs(calculated_capacity_per_min - self.people_per_minute) < 0.01,
        }

    def calculate_daily_visitors(self, wait_times: list) -> dict:
        """
        Calculate total daily visitors based on wait time progression.

        Algorithm:
        1. Initial value = first_wait_time × 24
        2. For each subsequent data point:
           - If wait_time increases: add (difference × 24) to total
           - If wait_time decreases: add 0 (ignore decrease)
           - If wait_time stays same: add (5 min × 24) = 120 to total

        Args:
            wait_times: List of wait times in minutes

        Returns:
            Dictionary with calculation details
        """
        if not wait_times or len(wait_times) == 0:
            return {
                "total_visitors": 0,
                "data_points": 0,
                "calculation_valid": False,
                "message": "No wait time data available",
            }

        total_visitors = wait_times[0] * self.people_per_minute
        interval_minutes = 5  # 5分ごとのデータ
        interval_capacity = interval_minutes * self.people_per_minute  # 120人

        for i in range(1, len(wait_times)):
            current_wait = wait_times[i]
            previous_wait = wait_times[i - 1]
            difference = current_wait - previous_wait

            if difference > 0:
                total_visitors += difference * self.people_per_minute
            elif difference == 0:
                total_visitors += interval_capacity
            else:  # difference < 0
                pass

        return {
            "total_visitors": int(total_visitors),
            "data_points": len(wait_times),
            "interval_minutes": interval_minutes,
            "first_wait_time": wait_times[0],
            "last_wait_time": wait_times[-1],
            "calculation_valid": True,
        }
