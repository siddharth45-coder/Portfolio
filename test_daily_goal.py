"""Unit tests for deterministic CodeStreak daily-goal calculations."""

import unittest
from datetime import date

from daily_goal import calculate_daily_goal


def day(day_date: str, count: int) -> dict:
    """Create a contribution-day record matching the GitHub API shape."""
    return {"date": day_date, "contributionCount": count}


class DailyGoalTests(unittest.TestCase):
    """Test zero, partial, complete, and above-target goal progress."""

    def setUp(self) -> None:
        self.today = date(2026, 8, 29)

    def test_zero_activity(self) -> None:
        goal = calculate_daily_goal([day("2026-08-28", 5)], self.today)
        self.assertEqual(goal["completed_count"], 0)
        self.assertFalse(goal["is_complete"])
        self.assertEqual(goal["progress_percent"], 0)

    def test_partially_completed_goal(self) -> None:
        goal = calculate_daily_goal([day("2026-08-29", 2)], self.today)
        self.assertEqual(goal["completed_count"], 2)
        self.assertFalse(goal["is_complete"])
        self.assertEqual(goal["progress_percent"], 67)

    def test_completed_goal(self) -> None:
        goal = calculate_daily_goal([day("2026-08-29", 3)], self.today)
        self.assertTrue(goal["is_complete"])
        self.assertEqual(goal["progress_percent"], 100)

    def test_activity_above_target(self) -> None:
        goal = calculate_daily_goal([day("2026-08-29", 6)], self.today)
        self.assertEqual(goal["completed_count"], 6)
        self.assertTrue(goal["is_complete"])
        self.assertEqual(goal["progress_percent"], 100)

    def test_repeated_calculation_does_not_duplicate_progress(self) -> None:
        contribution_days = [day("2026-08-29", 2)]
        self.assertEqual(
            calculate_daily_goal(contribution_days, self.today),
            calculate_daily_goal(contribution_days, self.today),
        )


if __name__ == "__main__":
    unittest.main()
