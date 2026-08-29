"""Track deterministic, session-scoped practice rewards after solved submissions."""

PRACTICE_XP_BY_DIFFICULTY = {"Easy": 10, "Medium": 20, "Hard": 30}


def award_practice_xp(rewarded_problem_ids: list[str], problem_id: str, difficulty: str) -> dict:
    """Return updated reward state; duplicate solved problems receive no XP twice."""
    rewarded_problem_ids = list(rewarded_problem_ids)
    if problem_id in rewarded_problem_ids:
        return {"rewarded_problem_ids": rewarded_problem_ids, "awarded_xp": 0}
    rewarded_problem_ids.append(problem_id)
    return {"rewarded_problem_ids": rewarded_problem_ids, "awarded_xp": PRACTICE_XP_BY_DIFFICULTY[difficulty]}


def calculate_practice_xp(rewarded_problem_ids: list[str], problems: list[dict]) -> int:
    """Calculate separate practice XP without changing GitHub-contribution XP."""
    difficulty_by_id = {problem["id"]: problem["difficulty"] for problem in problems}
    return sum(PRACTICE_XP_BY_DIFFICULTY[difficulty_by_id[problem_id]] for problem_id in rewarded_problem_ids if problem_id in difficulty_by_id)
