"""Unit tests for CodeStreak's extensible practice problem library."""

import unittest

from problem_library import PROBLEMS, get_practice_summary, get_problem, list_problems, validate_problems


class ProblemLibraryTests(unittest.TestCase):
    """Test validation, listing, filters, and summary progress."""

    def test_problem_data_is_valid(self) -> None:
        self.assertTrue(validate_problems())
        self.assertEqual(len(PROBLEMS), 10)

    def test_problem_listing(self) -> None:
        self.assertEqual(len(list_problems()), 10)
        self.assertEqual(get_problem("two-sum")["title"], "Two Sum")

    def test_search_by_title(self) -> None:
        self.assertEqual([problem["id"] for problem in list_problems(search="reverse")], ["reverse-string"])

    def test_difficulty_filtering(self) -> None:
        self.assertEqual(len(list_problems(difficulty="Easy")), 5)
        self.assertEqual(len(list_problems(difficulty="Hard")), 2)

    def test_topic_filtering(self) -> None:
        self.assertEqual(len(list_problems(topic="Arrays")), 3)

    def test_solved_and_unsolved_filtering(self) -> None:
        self.assertEqual(list_problems(status="solved"), [])
        self.assertEqual(len(list_problems(status="unsolved")), 10)

    def test_empty_filter_results(self) -> None:
        self.assertEqual(list_problems(search="not-a-real-problem"), [])

    def test_progress_calculation(self) -> None:
        summary = get_practice_summary()
        self.assertEqual((summary["total"], summary["solved"], summary["unsolved"]), (10, 0, 10))
        self.assertEqual(summary["completion_percent"], 0)
        self.assertEqual(summary["by_difficulty"], {"Easy": 5, "Medium": 3, "Hard": 2})


if __name__ == "__main__":
    unittest.main()
