"""Small unit tests for the streak calculation logic."""

import unittest
from datetime import date

from streak_calculator import calculate_streaks


def day(day_date: str, count: int) -> dict:
    """Create one contribution-day record like the GitHub API returns."""
    return {"date": day_date, "contributionCount": count}


class StreakCalculationTests(unittest.TestCase):
    """Test the rules used to calculate current and longest streaks."""

    def test_no_contributions(self) -> None:
        result = calculate_streaks(
            [day("2026-01-01", 0), day("2026-01-02", 0)], date(2026, 1, 2)
        )
        self.assertEqual(result, (0, 0))

    def test_one_day_streak(self) -> None:
        result = calculate_streaks([day("2026-01-02", 1)], date(2026, 1, 2))
        self.assertEqual(result, (1, 1))

    def test_multiple_consecutive_days(self) -> None:
        result = calculate_streaks(
            [day("2026-01-01", 2), day("2026-01-02", 1), day("2026-01-03", 4)],
            date(2026, 1, 3),
        )
        self.assertEqual(result, (3, 3))

    def test_zero_contribution_breaks_a_streak(self) -> None:
        result = calculate_streaks(
            [
                day("2026-01-01", 1),
                day("2026-01-02", 1),
                day("2026-01-03", 0),
                day("2026-01-04", 1),
            ],
            date(2026, 1, 4),
        )
        self.assertEqual(result, (1, 2))

    def test_today_contribution_is_included(self) -> None:
        result = calculate_streaks(
            [day("2026-01-04", 1), day("2026-01-05", 3)], date(2026, 1, 5)
        )
        self.assertEqual(result, (2, 2))

    def test_future_dates_are_not_counted(self) -> None:
        result = calculate_streaks(
            [day("2026-01-05", 1), day("2026-01-06", 2)], date(2026, 1, 5)
        )
        self.assertEqual(result, (1, 1))


if __name__ == "__main__":
    unittest.main()
