"""Validation and defaults for session-scoped practice preferences."""

from practice_analytics import TOPIC_DEFINITIONS

LANGUAGES = ("Python",)
DIFFICULTIES = ("Easy", "Medium", "Hard")
DEFAULT_PREFERENCES = {
    "language": "Python", "topics": [], "difficulty": "", "weekly_goal": 3,
}


def normalize_preferences(values: dict) -> dict:
    """Return safe, supported preferences without retaining arbitrary input."""
    topics = values.get("topics", [])
    if isinstance(topics, str):
        topics = [topics]
    try:
        weekly_goal = max(1, min(50, int(values.get("weekly_goal", 3))))
    except (TypeError, ValueError):
        weekly_goal = 3
    return {
        "language": values.get("language") if values.get("language") in LANGUAGES else "Python",
        "topics": [topic for topic in topics if topic in TOPIC_DEFINITIONS],
        "difficulty": values.get("difficulty") if values.get("difficulty") in DIFFICULTIES else "",
        "weekly_goal": weekly_goal,
    }
