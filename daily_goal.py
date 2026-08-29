"""Calculate daily coding-goal progress from GitHub contribution records."""

from datetime import date


DEFAULT_DAILY_TARGET = 3


def calculate_daily_goal(
    contribution_days: list[dict],
    today: date | None = None,
    target: int = DEFAULT_DAILY_TARGET,
) -> dict:
    """Return today's deterministic progress toward a contribution target.

    The target can be changed by a future setting without changing this logic.
    The function reads only the supplied calendar records and stores nothing,
    so refreshing the dashboard cannot duplicate progress.
    """
    if target < 1:
        raise ValueError("Daily target must be at least 1.")

    if today is None:
        today = date.today()

    completed_count = 0
    for day in contribution_days:
        try:
            day_date = date.fromisoformat(day["date"])
            contribution_count = int(day["contributionCount"])
        except (KeyError, TypeError, ValueError):
            continue

        if day_date == today:
            completed_count += max(contribution_count, 0)

    return {
        "completed_count": completed_count,
        "target": target,
        "is_complete": completed_count >= target,
        "progress_percent": min(100, round((completed_count / target) * 100)),
    }
