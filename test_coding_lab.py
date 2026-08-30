"""Focused integration tests for the Phase 6 Coding Lab foundation."""

import unittest
from unittest.mock import patch

from app import app


class CodingLabTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_default_lab_route_renders_editor_and_scene(self):
        response = self.client.get("/coding-lab")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"3D Coding Lab", response.data)
        self.assertIn(b"coding-lab-scene", response.data)
        self.assertIn(b"CodeMirror", response.data)

    def test_problem_specific_lab_loads_starter_code(self):
        response = self.client.get("/coding-lab/two-sum")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Two Sum", response.data)
        self.assertIn(b"def two_sum", response.data)

    def test_invalid_lab_problem_is_not_found(self):
        self.assertEqual(self.client.get("/coding-lab/not-a-problem").status_code, 404)

    def test_lab_run_reuses_existing_execution_path(self):
        response = self.client.post(
            "/coding-lab/sum-array/run", data={"code": "def sum_array(nums):\n    return sum(nums)"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"1 / 1 tests passed", response.data)

    @patch("app.save_solution_to_github")
    @patch("app.get_repository_name", return_value="owner/repository")
    @patch("app.get_github_profile", return_value={"login": "owner"})
    @patch("app.os.getenv", return_value="server-only-token")
    def test_successful_submit_awards_once_saves_and_updates_history(self, _token, _profile, _repository, save):
        save.return_value = {"saved": True, "unchanged": False, "message": "Solution saved to GitHub."}
        code = "def sum_array(nums):\n    return sum(nums)"
        response = self.client.post("/coding-lab/sum-array/submit", data={"code": code})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You earned 10 practice XP", response.data)
        self.assertIn(b"Solution saved to GitHub", response.data)
        self.assertNotIn(b"server-only-token", response.data)
        duplicate = self.client.post("/coding-lab/sum-array/submit", data={"code": code})
        self.assertIn(b"no duplicate XP", duplicate.data)
        self.assertEqual(save.call_count, 1)
        with self.client.session_transaction() as session:
            self.assertEqual(session["rewarded_problem_ids"], ["sum-array"])
            self.assertEqual(len(session["submission_history"]), 1)
            self.assertEqual(session["submission_history"][0]["github_status"], "Solution saved to GitHub.")

    def test_failed_submit_records_history_without_xp(self):
        response = self.client.post("/coding-lab/sum-array/submit", data={"code": "def sum_array(nums):\n    return 0"})
        self.assertIn(b"Submission failed", response.data)
        with self.client.session_transaction() as session:
            self.assertNotIn("rewarded_problem_ids", session)
            self.assertFalse(session["submission_history"][0]["passed"])

    @patch("app.save_solution_to_github", return_value={"saved": False, "unchanged": False, "message": "GitHub could not save the solution."})
    @patch("app.get_repository_name", return_value="owner/repository")
    @patch("app.get_github_profile", return_value={"login": "owner"})
    @patch("app.os.getenv", return_value="server-only-token")
    def test_github_save_failure_keeps_successful_submission(self, _token, _profile, _repository, _save):
        response = self.client.post("/coding-lab/sum-array/submit", data={"code": "def sum_array(nums):\n    return sum(nums)"})
        self.assertIn(b"GitHub could not save the solution", response.data)
        with self.client.session_transaction() as session:
            self.assertEqual(session["solved_problem_ids"], ["sum-array"])
            self.assertEqual(session["rewarded_problem_ids"], ["sum-array"])

    def test_existing_practice_page_links_to_lab(self):
        response = self.client.get("/practice")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"3D Coding Lab", response.data)


if __name__ == "__main__":
    unittest.main()
