"""Focused tests for execution, evaluation, rewards, and GitHub save helpers."""

import unittest
from unittest.mock import Mock, patch

from github_practice import build_practice_path, save_solution_to_github
from app import app
from practice_evaluator import evaluate_solution
from practice_rewards import award_practice_xp, calculate_practice_xp
from problem_library import PROBLEMS, get_problem


class PracticePlatformTests(unittest.TestCase):
    """Exercise server-side Practice integrations without network access."""

    def setUp(self):
        self.problem = get_problem("sum-array", include_tests=True)
        self.good_code = "def sum_array(nums):\n    return sum(nums)"

    def test_successful_submission(self):
        result = evaluate_solution(self.problem, self.good_code, include_hidden=True)
        self.assertTrue(result["is_solved"])

    def test_failed_submission(self):
        result = evaluate_solution(self.problem, "def sum_array(nums):\n    return 0", include_hidden=True)
        self.assertFalse(result["is_solved"])

    def test_syntax_and_runtime_errors(self):
        syntax = evaluate_solution(self.problem, "def sum_array(:\n    pass", False)
        runtime = evaluate_solution(self.problem, "def sum_array(nums):\n    return 1 / 0", False)
        self.assertEqual(syntax["status"], "syntax_error")
        self.assertEqual(runtime["status"], "runtime_error")

    def test_timeout(self):
        result = evaluate_solution(self.problem, "def sum_array(nums):\n    while True: pass", False)
        self.assertEqual(result["status"], "timeout")

    def test_practice_xp_and_duplicate_prevention(self):
        reward = award_practice_xp([], "sum-array", "Easy")
        duplicate = award_practice_xp(reward["rewarded_problem_ids"], "sum-array", "Easy")
        self.assertEqual((reward["awarded_xp"], duplicate["awarded_xp"]), (10, 0))
        self.assertEqual(calculate_practice_xp(reward["rewarded_problem_ids"], list(PROBLEMS)), 10)

    def test_github_path_generation(self):
        self.assertEqual(build_practice_path(get_problem("two-sum")), "practice/python/arrays/two-sum.py")

    def test_editor_problem_route(self):
        response = app.test_client().get("/practice/two-sum")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Python workspace", response.data)

    @patch("github_practice.requests")
    def test_github_save_skips_unchanged_content(self, requests_mock):
        existing = Mock(status_code=200)
        existing.json.return_value = {"content": "ZGVmIHgoKTogcGFzcw==", "sha": "abc"}
        requests_mock.get.return_value = existing
        result = save_solution_to_github("token", "owner", "repo", "practice/python/arrays/x.py", "def x(): pass")
        self.assertTrue(result["unchanged"])
        requests_mock.put.assert_not_called()


if __name__ == "__main__":
    unittest.main()
