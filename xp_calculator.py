"""Calculate deterministic XP and level information from contribution data."""


# Each tuple is (level number, XP needed to reach that level).
LEVEL_THRESHOLDS = (
    (1, 0),
    (2, 100),
    (3, 250),
    (4, 500),
    (5, 1000),
)


def calculate_xp(contribution_days: list[dict], current_streak: int) -> dict:
    """Return XP totals from a single contribution-calendar snapshot.

    This function changes no data and stores no running total. Calling it again
    with the same calendar produces the same result, so page refreshes cannot
    award duplicate XP.
    """
    total_contributions = 0
    coding_days = 0

    for day in contribution_days:
        try:
            contribution_count = int(day["contributionCount"])
        except (KeyError, TypeError, ValueError):
            continue

        # A positive count is both a contribution and a coding day.
        if contribution_count > 0:
            total_contributions += contribution_count
            coding_days += 1

    contribution_xp = total_contributions * 10
    coding_day_xp = coding_days * 25
    streak_xp = max(current_streak, 0) * 5
    total_xp = contribution_xp + coding_day_xp + streak_xp

    return {
        "total_xp": total_xp,
        "contribution_xp": contribution_xp,
        "coding_day_xp": coding_day_xp,
        "streak_xp": streak_xp,
    }


def calculate_level(total_xp: int) -> dict:
    """Return the current level and progress toward the next level."""
    total_xp = max(total_xp, 0)
    current_index = 0

    for index, (_, threshold) in enumerate(LEVEL_THRESHOLDS):
        if total_xp >= threshold:
            current_index = index
        else:
            break

    level, level_start_xp = LEVEL_THRESHOLDS[current_index]

    # Level 5 is currently the highest defined level.
    if current_index == len(LEVEL_THRESHOLDS) - 1:
        return {
            "level": level,
            "next_level": None,
            "xp_to_next_level": 0,
            "xp_progress": total_xp - level_start_xp,
            "xp_needed_for_level": 0,
            "progress_percent": 100,
        }

    next_level, next_level_xp = LEVEL_THRESHOLDS[current_index + 1]
    xp_needed_for_level = next_level_xp - level_start_xp
    xp_progress = total_xp - level_start_xp

    return {
        "level": level,
        "next_level": next_level,
        "xp_to_next_level": next_level_xp - total_xp,
        "xp_progress": xp_progress,
        "xp_needed_for_level": xp_needed_for_level,
        "progress_percent": round((xp_progress / xp_needed_for_level) * 100),
    }


def calculate_xp_summary(contribution_days: list[dict], current_streak: int) -> dict:
    """Combine the XP and level calculations for the dashboard."""
    xp_data = calculate_xp(contribution_days, current_streak)
    return {**xp_data, **calculate_level(xp_data["total_xp"])}
