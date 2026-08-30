"""Focused tests for Phase 5 personalization and advanced practice services."""

import unittest
from datetime import date

from app import app
from milestones import calculate_milestones
from practice_analytics import calculate_advanced_analytics, calculate_practice_statistics, calculate_topic_progress
from practice_preferences import normalize_preferences
from practice_rewards import award_practice_xp
from problem_library import PROBLEMS
from recommendations import recommend_problems
from weekly_challenge import get_weekly_challenge


class PhaseFiveTests(unittest.TestCase):
    def test_preferences_are_validated(self):
        prefs = normalize_preferences({"language": "Python", "topics": ["Arrays", "Bad"], "difficulty": "Hard", "weekly_goal": "8"})
        self.assertEqual(prefs, {"language": "Python", "topics": ["Arrays"], "difficulty": "Hard", "weekly_goal": 8})

    def test_recommendations_are_deterministic_and_filter_solved(self):
        prefs = normalize_preferences({"topics": ["Arrays"], "difficulty": "Medium"})
        first = recommend_problems(PROBLEMS, {"two-sum"}, prefs, [])
        second = recommend_problems(PROBLEMS, {"two-sum"}, prefs, [])
        self.assertEqual([item["id"] for item in first], [item["id"] for item in second])
        self.assertNotIn("two-sum", [item["id"] for item in first])

    def test_weekly_challenge_is_stable_and_does_not_create_extra_xp(self):
        monday = date(2026, 8, 24)
        sunday = date(2026, 8, 30)
        first = get_weekly_challenge(PROBLEMS, set(), monday)
        second = get_weekly_challenge(PROBLEMS, {first["problem"]["id"]}, sunday)
        self.assertEqual(first["problem"]["id"], second["problem"]["id"])
        reward = award_practice_xp([], first["problem"]["id"], first["problem"]["difficulty"])
        self.assertEqual(award_practice_xp(reward["rewarded_problem_ids"], first["problem"]["id"], first["problem"]["difficulty"])["awarded_xp"], 0)

    def test_analytics_and_milestones(self):
        solved = {"sum-array"}
        stats = calculate_practice_statistics(PROBLEMS, solved, ["sum-array"], [{"passed": True, "topic": "Arrays", "timestamp": "now"}])
        analytics = calculate_advanced_analytics(stats, [{"passed": True, "timestamp": "now"}])
        milestones = calculate_milestones(stats, calculate_topic_progress(PROBLEMS, solved), None)
        self.assertEqual((analytics["practice_xp"], len(analytics["xp_activity_points"])), (10, 1))
        self.assertTrue(milestones[0]["unlocked"])

    def test_progress_dashboard_and_preferences_route(self):
        client = app.test_client()
        response = client.post("/practice/preferences", data={"difficulty": "Easy", "topics": "Arrays", "weekly_goal": "4"})
        self.assertEqual(response.status_code, 200)
        for content in (b"Recommendations", b"Weekly Challenge", b"Goals & milestones", b"XP & progress analytics"):
            self.assertIn(content, response.data)


if __name__ == "__main__":
    unittest.main()
