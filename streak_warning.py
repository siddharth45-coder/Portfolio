"""Create a reusable, deterministic warning for an at-risk coding streak."""

from datetime import date


def calculate_streak_warning(
    contribution_days: list[dict], current_streak: int, today: date | None = None
) -> dict:
    """Return whether an active streak needs a contribution today.

    ``current_streak`` comes from the existing streak calculator. When it is
    positive, the user has a streak continuing through today or yesterday. The
    warning is needed only when that streak is active and today has no activity.
    This result is storage-free and suitable for future notification channels.
    """
    if today is None:
        today = date.today()

    today_contribution_count = 0
    for day in contribution_days:
        try:
            day_date = date.fromisoformat(day["date"])
            contribution_count = int(day["contributionCount"])
        except (KeyError, TypeError, ValueError):
            continue

        if day_date == today:
            today_contribution_count += max(contribution_count, 0)

    is_at_risk = current_streak > 0 and today_contribution_count == 0
    return {
        "is_at_risk": is_at_risk,
        "today_contribution_count": today_contribution_count,
        "message": "Your streak is at risk — make a contribution today."
        if is_at_risk
        else None,
    }
