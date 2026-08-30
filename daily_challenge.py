"""Deterministic daily challenge selection from the existing problem library."""

from datetime import date

from practice_rewards import PRACTICE_XP_BY_DIFFICULTY


def get_daily_challenge(problems: list[dict] | tuple[dict, ...], solved_ids: set[str], today: date | None = None) -> dict | None:
    """Select one stable challenge for a date without storing or randomizing it."""
    if not problems:
        return None
    today = today or date.today()
    problem = sorted(problems, key=lambda item: item["id"])[today.toordinal() % len(problems)]
    return {
        "date": today.isoformat(),
        "problem": dict(problem, is_solved=problem["id"] in solved_ids),
        # The reward is the existing per-problem practice XP, never extra XP.
        "xp_reward": PRACTICE_XP_BY_DIFFICULTY[problem["difficulty"]],
    }
