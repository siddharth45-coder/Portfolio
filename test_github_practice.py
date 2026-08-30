"""Focused tests for token-safe GitHub practice-folder saving."""

import unittest
from unittest.mock import Mock, patch

import requests

from github_practice import build_practice_path, save_solution_to_github
from problem_library import get_problem


class GitHubPracticeTests(unittest.TestCase):
    def test_path_generation(self):
        self.assertEqual(build_practice_path(get_problem("two-sum")), "practice/python/arrays/two-sum.py")

    @patch("github_practice.requests")
    def test_save_success_targets_branch_without_exposing_token(self, requests_mock):
        existing = Mock(status_code=404)
        saved = Mock(status_code=201)
        requests_mock.get.return_value = existing
        requests_mock.put.return_value = saved
        result = save_solution_to_github("secret-token", "owner", "repo", "practice/python/arrays/x.py", "def x(): pass", "main")
        self.assertTrue(result["saved"])
        self.assertNotIn("secret-token", result["message"])
        self.assertEqual(requests_mock.put.call_args.kwargs["json"]["branch"], "main")

    @patch("github_practice.requests")
    def test_authentication_and_api_failures_are_actionable(self, requests_mock):
        requests_mock.get.return_value = Mock(status_code=401)
        auth = save_solution_to_github("token", "owner", "repo", "path.py", "code")
        self.assertIn("authentication", auth["message"].lower())
        requests_mock.get.return_value = Mock(status_code=404)
        requests_mock.put.return_value = Mock(status_code=403)
        denied = save_solution_to_github("token", "owner", "repo", "path.py", "code")
        self.assertIn("Contents read/write", denied["message"])

    @patch("github_practice.requests.get", side_effect=requests.RequestException())
    def test_network_failure_is_safe(self, _get):
        result = save_solution_to_github("token", "owner", "repo", "path.py", "code")
        self.assertFalse(result["saved"])
        self.assertIn("could not be reached", result["message"])


if __name__ == "__main__":
    unittest.main()
