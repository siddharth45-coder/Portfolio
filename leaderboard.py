"""Rank real CodeStreak user records for future leaderboard data sources."""


# More ranking modes can be added here without changing the dashboard contract.
RANKING_TYPES = {"total_xp"}


def rank_leaderboard(
    users: list[dict],
    current_username: str | None = None,
    ranking_type: str = "total_xp",
) -> list[dict]:
    """Return ranked user records using deterministic CodeStreak ordering.

    Callers supply only real user records from an eventual multi-user source.
    The current implementation ranks by total XP, then total contributions,
    and finally username alphabetically. It stores and creates no users.
    """
    if ranking_type not in RANKING_TYPES:
        raise ValueError(f"Unsupported ranking type: {ranking_type}")

    ranked_users = []
    for user in users:
        try:
            username = str(user["username"])
            total_xp = max(int(user["total_xp"]), 0)
            level = max(int(user["level"]), 1)
            total_contributions = max(int(user["total_contributions"]), 0)
            current_streak = max(int(user["current_streak"]), 0)
        except (KeyError, TypeError, ValueError):
            continue

        if username:
            ranked_users.append(
                {
                    "username": username,
                    "total_xp": total_xp,
                    "level": level,
                    "total_contributions": total_contributions,
                    "current_streak": current_streak,
                }
            )

    ranked_users.sort(
        key=lambda user: (
            -user["total_xp"],
            -user["total_contributions"],
            user["username"].casefold(),
        )
    )

    for rank, user in enumerate(ranked_users, start=1):
        user["rank"] = rank
        user["is_current_user"] = user["username"] == current_username

    return ranked_users
