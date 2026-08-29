"""Define and calculate CodeStreak badges from existing activity metrics."""


# Each badge has a stable identifier, its progress source, and its target.
# Adding a future badge only requires another entry in this catalog.
BADGE_DEFINITIONS = (
    {
        "id": "first-contribution",
        "title": "First Contribution",
        "description": "Make your first GitHub contribution.",
        "metric": "contributions",
        "target": 1,
    },
    {
        "id": "five-contributions",
        "title": "5 Contributions",
        "description": "Make 5 GitHub contributions.",
        "metric": "contributions",
        "target": 5,
    },
    {
        "id": "ten-contributions",
        "title": "10 Contributions",
        "description": "Make 10 GitHub contributions.",
        "metric": "contributions",
        "target": 10,
    },
    {
        "id": "three-day-streak",
        "title": "3 Day Streak",
        "description": "Reach a 3-day coding streak.",
        "metric": "longest_streak",
        "target": 3,
    },
    {
        "id": "seven-day-streak",
        "title": "7 Day Streak",
        "description": "Reach a 7-day coding streak.",
        "metric": "longest_streak",
        "target": 7,
    },
    {
        "id": "fourteen-day-streak",
        "title": "14 Day Streak",
        "description": "Reach a 14-day coding streak.",
        "metric": "longest_streak",
        "target": 14,
    },
    {
        "id": "thirty-day-streak",
        "title": "30 Day Streak",
        "description": "Reach a 30-day coding streak.",
        "metric": "longest_streak",
        "target": 30,
    },
    {
        "id": "level-two",
        "title": "Level 2",
        "description": "Reach Level 2.",
        "metric": "level",
        "target": 2,
    },
    {
        "id": "level-five",
        "title": "Level 5",
        "description": "Reach Level 5.",
        "metric": "level",
        "target": 5,
    },
)


def calculate_badges(
    total_contributions: int, longest_streak: int, level: int
) -> list[dict]:
    """Return a deterministic unlocked/locked record for every badge.

    The function has no saved state: the same GitHub activity metrics always
    generate the same badges, so dashboard refreshes cannot create duplicates.
    """
    metrics = {
        "contributions": max(total_contributions, 0),
        "longest_streak": max(longest_streak, 0),
        "level": max(level, 0),
    }
    badges = []

    for definition in BADGE_DEFINITIONS:
        value = metrics[definition["metric"]]
        target = definition["target"]
        badges.append(
            {
                **definition,
                "value": value,
                "unlocked": value >= target,
                "progress_percent": min(100, round((value / target) * 100)),
            }
        )

    return badges
