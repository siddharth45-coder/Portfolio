"""Deterministic milestones that can later feed badges or a skill tree."""


def calculate_milestones(statistics: dict, topic_progress: list[dict], weekly_challenge: dict | None) -> list[dict]:
    """Return display-ready unlocked status without persisting duplicate rewards."""
    completed_topics = sum(item["total"] > 0 and item["solved"] == item["total"] for item in topic_progress)
    return [
        {"name": "First solve", "detail": "Solve 1 problem", "unlocked": statistics["solved"] >= 1},
        {"name": "Practice regular", "detail": "Solve 5 problems", "unlocked": statistics["solved"] >= 5},
        {"name": "XP builder", "detail": "Earn 100 practice XP", "unlocked": statistics["practice_xp"] >= 100},
        {"name": "Hard solver", "detail": "Solve a Hard problem", "unlocked": statistics["solved_by_difficulty"]["Hard"] >= 1},
        {"name": "Topic complete", "detail": "Complete one topic", "unlocked": completed_topics >= 1},
        {"name": "Weekly challenger", "detail": "Solve this week's challenge", "unlocked": bool(weekly_challenge and weekly_challenge["problem"]["is_solved"])},
    ]
