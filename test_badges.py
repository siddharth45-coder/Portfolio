"""Unit tests for deterministic CodeStreak badge calculations."""

import unittest

from badges import calculate_badges


def badge_by_id(badges: list[dict], badge_id: str) -> dict:
    """Find a badge by its stable identifier."""
    return next(badge for badge in badges if badge["id"] == badge_id)


class BadgeCalculationTests(unittest.TestCase):
    """Test contribution, streak, level, and repeatable badge results."""

    def test_zero_activity_leaves_badges_locked(self) -> None:
        badges = calculate_badges(0, 0, 1)
        self.assertFalse(any(badge["unlocked"] for badge in badges))

    def test_contribution_badges_unlock_at_thresholds(self) -> None:
        badges = calculate_badges(5, 0, 1)
        self.assertTrue(badge_by_id(badges, "first-contribution")["unlocked"])
        self.assertTrue(badge_by_id(badges, "five-contributions")["unlocked"])
        self.assertFalse(badge_by_id(badges, "ten-contributions")["unlocked"])

    def test_streak_badges_use_longest_streak(self) -> None:
        badges = calculate_badges(0, 14, 1)
        self.assertTrue(badge_by_id(badges, "three-day-streak")["unlocked"])
        self.assertTrue(badge_by_id(badges, "seven-day-streak")["unlocked"])
        self.assertTrue(badge_by_id(badges, "fourteen-day-streak")["unlocked"])
        self.assertFalse(badge_by_id(badges, "thirty-day-streak")["unlocked"])

    def test_level_badges_unlock_at_thresholds(self) -> None:
        badges = calculate_badges(0, 0, 5)
        self.assertTrue(badge_by_id(badges, "level-two")["unlocked"])
        self.assertTrue(badge_by_id(badges, "level-five")["unlocked"])

    def test_locked_badge_reports_progress(self) -> None:
        badges = calculate_badges(7, 0, 1)
        ten_contributions = badge_by_id(badges, "ten-contributions")
        self.assertEqual(ten_contributions["value"], 7)
        self.assertEqual(ten_contributions["progress_percent"], 70)

    def test_repeated_calculation_does_not_duplicate_badges(self) -> None:
        first_result = calculate_badges(10, 3, 2)
        second_result = calculate_badges(10, 3, 2)
        self.assertEqual(first_result, second_result)
        self.assertEqual(len(first_result), 9)


if __name__ == "__main__":
    unittest.main()
