"""Stable weekly challenge derived from ISO week and existing problem data."""

from datetime import date

from practice_rewards import PRACTICE_XP_BY_DIFFICULTY


def get_weekly_challenge(problems: list[dict] | tuple[dict, ...], solved_ids: set[str], today: date | None = None) -> dict | None:
    """Return one challenge for an ISO week; no separate XP is awarded."""
    if not problems:
        return None
    today = today or date.today()
    year, week, _ = today.isocalendar()
    ordered = sorted(problems, key=lambda item: item["id"])
    problem = ordered[(year * 53 + week) % len(ordered)]
    return {
        "week": f"{year}-W{week:02d}",
        "problem": dict(problem, is_solved=problem["id"] in solved_ids),
        "xp_reward": PRACTICE_XP_BY_DIFFICULTY[problem["difficulty"]],
    }
