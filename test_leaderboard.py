"""Unit tests for deterministic CodeStreak leaderboard ranking."""

import unittest

from leaderboard import rank_leaderboard


def user(
    username: str, total_xp: int, contributions: int, level: int = 1, streak: int = 0
) -> dict:
    """Create a real-user-shaped leaderboard record for a unit test."""
    return {
        "username": username,
        "total_xp": total_xp,
        "level": level,
        "total_contributions": contributions,
        "current_streak": streak,
    }


class LeaderboardTests(unittest.TestCase):
    """Test ranking order, highlighting, and an honest empty state."""

    def test_xp_descending_order(self) -> None:
        leaderboard = rank_leaderboard(
            [user("alex", 200, 5), user("bea", 350, 2), user("cam", 100, 10)]
        )
        self.assertEqual([entry["username"] for entry in leaderboard], ["bea", "alex", "cam"])

    def test_contribution_tie_breaker(self) -> None:
        leaderboard = rank_leaderboard(
            [user("alex", 200, 5), user("bea", 200, 8)]
        )
        self.assertEqual([entry["username"] for entry in leaderboard], ["bea", "alex"])

    def test_username_tie_breaker(self) -> None:
        leaderboard = rank_leaderboard(
            [user("zoe", 200, 5), user("alex", 200, 5)]
        )
        self.assertEqual([entry["username"] for entry in leaderboard], ["alex", "zoe"])

    def test_current_user_is_highlighted(self) -> None:
        leaderboard = rank_leaderboard(
            [user("alex", 200, 5), user("bea", 300, 4)], current_username="alex"
        )
        current_user = next(entry for entry in leaderboard if entry["is_current_user"])
        self.assertEqual((current_user["username"], current_user["rank"]), ("alex", 2))

    def test_empty_leaderboard(self) -> None:
        self.assertEqual(rank_leaderboard([]), [])


if __name__ == "__main__":
    unittest.main()
