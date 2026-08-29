"""Unit tests for CodeStreak XP and level calculations."""

import unittest

from xp_calculator import calculate_level, calculate_xp, calculate_xp_summary


def day(day_date: str, count: int) -> dict:
    """Create a contribution-day record matching the GitHub API shape."""
    return {"date": day_date, "contributionCount": count}


class XpCalculationTests(unittest.TestCase):
    """Test each of the Phase 2 XP and level rules."""

    def test_zero_contributions(self) -> None:
        summary = calculate_xp_summary([day("2026-01-01", 0)], 0)
        self.assertEqual(summary["total_xp"], 0)
        self.assertEqual(summary["level"], 1)

    def test_one_contribution(self) -> None:
        xp_data = calculate_xp([day("2026-01-01", 1)], 0)
        self.assertEqual(xp_data["total_xp"], 35)

    def test_multiple_contributions(self) -> None:
        xp_data = calculate_xp([day("2026-01-01", 3)], 0)
        self.assertEqual(xp_data["total_xp"], 55)

    def test_multiple_coding_days(self) -> None:
        xp_data = calculate_xp(
            [day("2026-01-01", 1), day("2026-01-02", 2), day("2026-01-03", 0)],
            0,
        )
        self.assertEqual(xp_data["total_xp"], 80)

    def test_streak_xp(self) -> None:
        xp_data = calculate_xp([], 3)
        self.assertEqual(xp_data["streak_xp"], 15)
        self.assertEqual(xp_data["total_xp"], 15)

    def test_level_one(self) -> None:
        level_data = calculate_level(99)
        self.assertEqual((level_data["level"], level_data["xp_to_next_level"]), (1, 1))

    def test_level_two(self) -> None:
        level_data = calculate_level(100)
        self.assertEqual((level_data["level"], level_data["next_level"]), (2, 3))

    def test_level_three_and_higher(self) -> None:
        self.assertEqual(calculate_level(250)["level"], 3)
        self.assertEqual(calculate_level(1000)["level"], 5)

    def test_xp_exactly_on_a_level_threshold(self) -> None:
        level_data = calculate_level(500)
        self.assertEqual(level_data["level"], 4)
        self.assertEqual(level_data["xp_progress"], 0)

    def test_repeated_calculation_does_not_add_xp(self) -> None:
        contribution_days = [day("2026-01-01", 2), day("2026-01-02", 1)]
        first_result = calculate_xp_summary(contribution_days, 2)
        second_result = calculate_xp_summary(contribution_days, 2)
        self.assertEqual(first_result, second_result)


if __name__ == "__main__":
    unittest.main()
