"""A small, extensible library of coding-practice problems for CodeStreak."""


DIFFICULTIES = ("Easy", "Medium", "Hard")
REQUIRED_PROBLEM_FIELDS = (
    "id", "title", "short_description", "difficulty", "topic", "language",
    "problem_statement", "example_input", "example_output", "constraints",
    "starter_code", "is_solved",
)


PROBLEMS = (
    {
        "id": "sum-array", "title": "Sum an Array", "short_description": "Return the total of all numbers in a list.",
        "difficulty": "Easy", "topic": "Arrays", "language": "Python", "is_solved": False,
        "problem_statement": "Write a function that returns the sum of every integer in nums.",
        "example_input": "nums = [2, 4, 6]", "example_output": "12",
        "constraints": "1 <= len(nums) <= 1000; -10,000 <= nums[i] <= 10,000",
        "starter_code": "def sum_array(nums):\n    # Write your solution here\n    pass",
    },
    {
        "id": "reverse-string", "title": "Reverse a String", "short_description": "Return a string with its characters in reverse order.",
        "difficulty": "Easy", "topic": "Strings", "language": "Python", "is_solved": False,
        "problem_statement": "Write a function that returns text reversed.",
        "example_input": "text = 'code'", "example_output": "'edoc'",
        "constraints": "0 <= len(text) <= 10,000", "starter_code": "def reverse_string(text):\n    # Write your solution here\n    pass",
    },
    {
        "id": "count-vowels", "title": "Count Vowels", "short_description": "Count vowels in a string, ignoring letter case.",
        "difficulty": "Easy", "topic": "Loops", "language": "Python", "is_solved": False,
        "problem_statement": "Return how many characters in text are a, e, i, o, or u.",
        "example_input": "text = 'CodeStreak'", "example_output": "4",
        "constraints": "0 <= len(text) <= 10,000", "starter_code": "def count_vowels(text):\n    # Write your solution here\n    pass",
    },
    {
        "id": "find-maximum", "title": "Find the Maximum", "short_description": "Find the largest number in a non-empty list.",
        "difficulty": "Easy", "topic": "Functions", "language": "Python", "is_solved": False,
        "problem_statement": "Return the largest integer in nums without using max().",
        "example_input": "nums = [3, 9, 2, 7]", "example_output": "9",
        "constraints": "1 <= len(nums) <= 1000", "starter_code": "def find_maximum(nums):\n    # Write your solution here\n    pass",
    },
    {
        "id": "linear-search", "title": "Linear Search", "short_description": "Return the index of a target value, or -1 when absent.",
        "difficulty": "Easy", "topic": "Searching", "language": "Python", "is_solved": False,
        "problem_statement": "Search nums from left to right and return target's first index.",
        "example_input": "nums = [5, 2, 8], target = 2", "example_output": "1",
        "constraints": "0 <= len(nums) <= 1000", "starter_code": "def linear_search(nums, target):\n    # Write your solution here\n    pass",
    },
    {
        "id": "two-sum", "title": "Two Sum", "short_description": "Find indices of two numbers that add to a target.",
        "difficulty": "Medium", "topic": "Arrays", "language": "Python", "is_solved": False,
        "problem_statement": "Return the indices of two distinct values in nums whose sum equals target.",
        "example_input": "nums = [2, 7, 11, 15], target = 9", "example_output": "[0, 1]",
        "constraints": "2 <= len(nums) <= 10,000; exactly one answer exists", "starter_code": "def two_sum(nums, target):\n    # Write your solution here\n    pass",
    },
    {
        "id": "palindrome-check", "title": "Palindrome Check", "short_description": "Check whether text reads the same forward and backward.",
        "difficulty": "Medium", "topic": "Strings", "language": "Python", "is_solved": False,
        "problem_statement": "Return True when text is a palindrome after ignoring case and non-alphanumeric characters.",
        "example_input": "text = 'Never odd or even'", "example_output": "True",
        "constraints": "0 <= len(text) <= 10,000", "starter_code": "def is_palindrome(text):\n    # Write your solution here\n    pass",
    },
    {
        "id": "merge-sort", "title": "Merge Sort", "short_description": "Sort a list using the merge-sort algorithm.",
        "difficulty": "Medium", "topic": "Sorting", "language": "Python", "is_solved": False,
        "problem_statement": "Return a new sorted list using merge sort; do not call sorted() or list.sort().",
        "example_input": "nums = [4, 1, 3, 2]", "example_output": "[1, 2, 3, 4]",
        "constraints": "0 <= len(nums) <= 10,000", "starter_code": "def merge_sort(nums):\n    # Write your solution here\n    pass",
    },
    {
        "id": "first-duplicate", "title": "First Duplicate", "short_description": "Find the first value that appears twice while scanning a list.",
        "difficulty": "Hard", "topic": "Arrays", "language": "Python", "is_solved": False,
        "problem_statement": "Return the first duplicate value encountered from left to right, or -1 if none exists.",
        "example_input": "nums = [2, 1, 3, 5, 3, 2]", "example_output": "3",
        "constraints": "1 <= len(nums) <= 100,000", "starter_code": "def first_duplicate(nums):\n    # Write your solution here\n    pass",
    },
    {
        "id": "binary-search-range", "title": "Binary Search Range", "short_description": "Find the first and last positions of a target in a sorted list.",
        "difficulty": "Hard", "topic": "Searching", "language": "Python", "is_solved": False,
        "problem_statement": "Return [first_index, last_index] for target in sorted nums, or [-1, -1] if absent.",
        "example_input": "nums = [1, 2, 2, 2, 4], target = 2", "example_output": "[1, 3]",
        "constraints": "0 <= len(nums) <= 100,000; nums is sorted", "starter_code": "def search_range(nums, target):\n    # Write your solution here\n    pass",
    },
)


def validate_problems(problems: tuple[dict, ...] | list[dict] = PROBLEMS) -> bool:
    """Validate the library shape so future additions remain compatible."""
    problem_ids = set()
    for problem in problems:
        if not all(problem.get(field) is not None for field in REQUIRED_PROBLEM_FIELDS):
            return False
        if problem["id"] in problem_ids or problem["difficulty"] not in DIFFICULTIES:
            return False
        if not isinstance(problem["is_solved"], bool):
            return False
        problem_ids.add(problem["id"])
    return True


def list_problems(
    search: str = "", difficulty: str = "", topic: str = "", status: str = ""
) -> list[dict]:
    """Return library problems matching optional title, category, and state filters."""
    search = search.strip().casefold()
    problems = list(PROBLEMS)
    if search:
        problems = [problem for problem in problems if search in problem["title"].casefold()]
    if difficulty in DIFFICULTIES:
        problems = [problem for problem in problems if problem["difficulty"] == difficulty]
    if topic:
        problems = [problem for problem in problems if problem["topic"] == topic]
    if status == "solved":
        problems = [problem for problem in problems if problem["is_solved"]]
    elif status == "unsolved":
        problems = [problem for problem in problems if not problem["is_solved"]]
    return problems


def get_problem(problem_id: str) -> dict | None:
    """Find one problem by its stable ID."""
    return next((problem for problem in PROBLEMS if problem["id"] == problem_id), None)


def get_practice_summary() -> dict:
    """Return display-ready totals and groupings for the practice dashboard."""
    total = len(PROBLEMS)
    solved = sum(problem["is_solved"] for problem in PROBLEMS)
    by_difficulty = {level: sum(problem["difficulty"] == level for problem in PROBLEMS) for level in DIFFICULTIES}
    topics = sorted({problem["topic"] for problem in PROBLEMS})
    by_topic = {topic: sum(problem["topic"] == topic for problem in PROBLEMS) for topic in topics}
    return {
        "total": total, "solved": solved, "unsolved": total - solved,
        "completion_percent": round((solved / total) * 100) if total else 0,
        "by_difficulty": by_difficulty, "by_topic": by_topic,
    }
