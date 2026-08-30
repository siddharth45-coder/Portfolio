"""Deterministic unsolved-problem recommendations for the practice library."""

DIFFICULTY_ORDER = {"Easy": 0, "Medium": 1, "Hard": 2}


def recommend_problems(problems: list[dict] | tuple[dict, ...], solved_ids: set[str], preferences: dict, submissions: list[dict], limit: int = 3) -> list[dict]:
    """Rank unsolved problems predictably from preferences and activity history."""
    attempted_topics = {item.get("topic") for item in submissions}

    def score(problem: dict) -> tuple:
        # Preferred language/topic/difficulty lead; previously attempted topics
        # follow, then the stable difficulty-title ordering breaks all ties.
        return (
            0 if problem["language"] == preferences["language"] else 1,
            0 if problem["topic"] in preferences["topics"] else 1,
            0 if not preferences["difficulty"] or problem["difficulty"] == preferences["difficulty"] else 1,
            0 if problem["topic"] in attempted_topics else 1,
            DIFFICULTY_ORDER[problem["difficulty"]], problem["title"].casefold(),
        )

    unsolved = [problem for problem in problems if problem["id"] not in solved_ids]
    return [dict(problem) for problem in sorted(unsolved, key=score)[:limit]]
