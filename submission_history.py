"""Small, session-scoped submission-history helpers."""

from datetime import datetime, timezone


MAX_SUBMISSIONS = 20


def record_submission(
    history: list[dict], problem: dict, result: dict,
    xp_earned: int = 0, github_status: str | None = None,
) -> list[dict]:
    """Add a safe submission summary; hidden tests and source code stay private."""
    entry = {
        "problem_id": problem["id"], "title": problem["title"],
        "topic": problem["topic"], "difficulty": problem["difficulty"],
        "language": problem["language"],
        "result": result["status"], "passed": result["is_solved"],
        "execution_ms": result.get("execution_ms"),
        "xp_earned": xp_earned, "github_status": github_status,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    return ([entry] + list(history))[:MAX_SUBMISSIONS]
