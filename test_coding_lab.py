"""Focused integration tests for the Phase 6 Coding Lab foundation."""

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
        self.assertIn(b"1 / 1 public tests passed", response.data)

    def test_existing_practice_page_links_to_lab(self):
        response = self.client.get("/practice")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"3D Coding Lab", response.data)


if __name__ == "__main__":
    unittest.main()
