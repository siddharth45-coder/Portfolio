"""Focused integration tests for the Coding Lab."""

import unittest

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

    def test_successful_submit_awards_once_without_github_push(self):
        code = "def sum_array(nums):\n    return sum(nums)"
        response = self.client.post("/coding-lab/sum-array/submit", data={"code": code})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You earned 10 practice XP", response.data)
        self.assertNotIn(b"Solution saved to GitHub", response.data)
        self.assertNotIn(b"GitHub commit", response.data)
        duplicate = self.client.post("/coding-lab/sum-array/submit", data={"code": code})
        self.assertIn(b"no duplicate XP", duplicate.data)
        with self.client.session_transaction() as session:
            self.assertEqual(session["rewarded_problem_ids"], ["sum-array"])
            self.assertEqual(len(session["submission_history"]), 1)

    def test_failed_submit_records_history_without_xp(self):
        response = self.client.post("/coding-lab/sum-array/submit", data={"code": "def sum_array(nums):\n    return 0"})
        self.assertIn(b"Submission failed", response.data)
        with self.client.session_transaction() as session:
            self.assertNotIn("rewarded_problem_ids", session)
            self.assertFalse(session["submission_history"][0]["passed"])

    def test_practice_page_has_no_github_save_button(self):
        response = self.client.get("/practice/sum-array")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Save to GitHub", response.data)

    def test_existing_practice_page_links_to_lab(self):
        response = self.client.get("/practice")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"3D Coding Lab", response.data)


if __name__ == "__main__":
    unittest.main()
