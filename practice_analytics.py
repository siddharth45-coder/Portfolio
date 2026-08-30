"""Reusable statistics and skill-progress helpers for the practice platform."""

from collections import Counter

from practice_rewards import calculate_practice_xp


# Topics are defined independently of the current library so new problems can
# use them without changing dashboard logic. Topics with no problems show 0%.
TOPIC_DEFINITIONS = (
    "Algorithms", "Arrays", "Data Structures", "Functions", "Loops",
    "Math", "Recursion", "Searching", "Sorting", "Strings",
)
DIFFICULTIES = ("Easy", "Medium", "Hard")


def calculate_topic_progress(problems: list[dict] | tuple[dict, ...], solved_ids: set[str]) -> list[dict]:
    """Return stable, display-ready progress for every supported topic."""
    progress = []
    for topic in TOPIC_DEFINITIONS:
        topic_problems = [problem for problem in problems if problem["topic"] == topic]
        total = len(topic_problems)
        solved = sum(problem["id"] in solved_ids for problem in topic_problems)
        progress.append({
            "name": topic,
            "total": total,
            "solved": solved,
            "completion_percent": round(solved / total * 100) if total else 0,
            "difficulty_distribution": {
                difficulty: sum(problem["difficulty"] == difficulty for problem in topic_problems)
                for difficulty in DIFFICULTIES
            },
        })
    return progress


def calculate_practice_statistics(
    problems: list[dict] | tuple[dict, ...], solved_ids: set[str],
    rewarded_ids: list[str], submissions: list[dict],
) -> dict:
    """Calculate deterministic user statistics from library and session data."""
    total = len(problems)
    solved_by_difficulty = {
        difficulty: sum(
            problem["id"] in solved_ids and problem["difficulty"] == difficulty
            for problem in problems
        ) for difficulty in DIFFICULTIES
    }
    successes = sum(submission.get("passed", False) for submission in submissions)
    topic_counts = Counter(submission["topic"] for submission in submissions if submission.get("topic"))
    most_practiced = [topic for topic, count in sorted(topic_counts.items()) if count == max(topic_counts.values())] if topic_counts else []
    return {
        "total": total,
        "solved": len(solved_ids),
        "unsolved": max(0, total - len(solved_ids)),
        "completion_percent": round(len(solved_ids) / total * 100) if total else 0,
        "solved_by_difficulty": solved_by_difficulty,
        "practice_xp": calculate_practice_xp(rewarded_ids, list(problems)),
        "submission_count": len(submissions),
        "successful_submissions": successes,
        "success_rate": round(successes / len(submissions) * 100) if submissions else 0,
        "most_practiced_topics": most_practiced,
    }
