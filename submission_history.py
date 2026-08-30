"""Small, session-scoped submission-history helpers."""

from datetime import datetime, timezone


MAX_SUBMISSIONS = 20


def record_submission(history: list[dict], problem: dict, result: dict) -> list[dict]:
    """Add a safe submission summary; hidden tests and source code stay private."""
    entry = {
        "problem_id": problem["id"], "title": problem["title"],
        "topic": problem["topic"], "language": problem["language"],
        "result": result["status"], "passed": result["is_solved"],
        "execution_ms": result.get("execution_ms"),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    return ([entry] + list(history))[:MAX_SUBMISSIONS]
