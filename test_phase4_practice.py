"""Tests for Phase 4 topic, challenge, history, and statistics services."""

import unittest
from datetime import date

from app import app
from daily_challenge import get_daily_challenge
from practice_analytics import TOPIC_DEFINITIONS, calculate_practice_statistics, calculate_topic_progress
from problem_library import PROBLEMS, list_problems
from submission_history import record_submission


class PhaseFourPracticeTests(unittest.TestCase):
    def test_topic_definitions_and_filtering(self):
        self.assertIn("Math", TOPIC_DEFINITIONS)
        self.assertEqual([item["id"] for item in list_problems(topic="Sorting")], ["merge-sort"])

    def test_topic_progress_and_statistics(self):
        solved = {"sum-array", "two-sum"}
        progress = {item["name"]: item for item in calculate_topic_progress(PROBLEMS, solved)}
        self.assertEqual((progress["Arrays"]["solved"], progress["Arrays"]["total"]), (2, 3))
        history = [{"passed": True, "topic": "Arrays"}, {"passed": False, "topic": "Strings"}]
        stats = calculate_practice_statistics(PROBLEMS, solved, ["sum-array", "two-sum"], history)
        self.assertEqual((stats["solved"], stats["practice_xp"], stats["success_rate"]), (2, 30, 50))
        self.assertEqual(stats["most_practiced_topics"], ["Arrays", "Strings"])

    def test_daily_challenge_is_deterministic_and_uses_existing_xp(self):
        day = date(2026, 8, 30)
        first = get_daily_challenge(PROBLEMS, set(), day)
        second = get_daily_challenge(PROBLEMS, {first["problem"]["id"]}, day)
        self.assertEqual(first["problem"]["id"], second["problem"]["id"])
        self.assertTrue(second["problem"]["is_solved"])
        self.assertIn(second["xp_reward"], (10, 20, 30))

    def test_submission_history_records_safe_success_and_failure(self):
        problem = PROBLEMS[0]
        success = record_submission([], problem, {"status": "ok", "is_solved": True, "execution_ms": 12.5})
        history = record_submission(success, problem, {"status": "runtime_error", "is_solved": False, "execution_ms": 4})
        self.assertEqual((len(history), history[0]["passed"], history[1]["passed"]), (2, False, True))
        self.assertNotIn("source", history[0])

    def test_practice_route_displays_phase_four_sections(self):
        response = app.test_client().get("/practice")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Daily Challenge", response.data)
        self.assertIn(b"Submission history", response.data)
        self.assertIn(b"Topic progress", response.data)


if __name__ == "__main__":
    unittest.main()
