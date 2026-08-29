"""Unit tests for CodeStreak's deterministic streak-warning logic."""

import unittest
from datetime import date

from streak_calculator import calculate_streaks
from streak_warning import calculate_streak_warning


def day(day_date: str, count: int) -> dict:
    """Create a contribution-day record matching the GitHub API shape."""
    return {"date": day_date, "contributionCount": count}


class StreakWarningTests(unittest.TestCase):
    """Test when an active streak should and should not show a warning."""

    def setUp(self) -> None:
        self.today = date(2026, 8, 29)

    def test_active_streak_without_contribution_today_shows_warning(self) -> None:
        contribution_days = [day("2026-08-28", 1)]
        current_streak, _ = calculate_streaks(contribution_days, self.today)
        warning = calculate_streak_warning(contribution_days, current_streak, self.today)
        self.assertTrue(warning["is_at_risk"])

    def test_active_streak_with_contribution_today_has_no_warning(self) -> None:
        contribution_days = [day("2026-08-28", 1), day("2026-08-29", 2)]
        current_streak, _ = calculate_streaks(contribution_days, self.today)
        warning = calculate_streak_warning(contribution_days, current_streak, self.today)
        self.assertFalse(warning["is_at_risk"])

    def test_no_active_streak_has_no_warning(self) -> None:
        contribution_days = [day("2026-08-27", 1), day("2026-08-28", 0)]
        current_streak, _ = calculate_streaks(contribution_days, self.today)
        warning = calculate_streak_warning(contribution_days, current_streak, self.today)
        self.assertFalse(warning["is_at_risk"])

    def test_consecutive_days_ending_yesterday_are_at_risk(self) -> None:
        contribution_days = [
            day("2026-08-26", 1),
            day("2026-08-27", 1),
            day("2026-08-28", 1),
            day("2026-08-29", 0),
        ]
        current_streak, _ = calculate_streaks(contribution_days, self.today)
        warning = calculate_streak_warning(contribution_days, current_streak, self.today)
        self.assertEqual(current_streak, 3)
        self.assertTrue(warning["is_at_risk"])


if __name__ == "__main__":
    unittest.main()
