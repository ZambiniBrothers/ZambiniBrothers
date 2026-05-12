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
