"""Calculate coding streaks from GitHub contribution calendar data."""

import sys
from datetime import date, timedelta

from contributions_api import get_contribution_calendar, get_contribution_days


def calculate_streaks(
    contribution_days: list[dict], today: date | None = None
) -> tuple[int, int]:
    """Return the current and longest streak from daily contribution records.

    A positive contribution count makes a coding day. Missing dates and days with
    zero contributions break a streak. The optional ``today`` value makes this
    function easy to test without depending on the computer's clock.
    """
    if today is None:
        today = date.today()

    # Store counts by date, skipping invalid or future records.
    counts_by_date: dict[date, int] = {}
    for day in contribution_days:
        try:
            day_date = date.fromisoformat(day["date"])
            contribution_count = int(day["contributionCount"])
        except (KeyError, TypeError, ValueError):
            continue

        if day_date <= today:
            counts_by_date[day_date] = contribution_count

    if not counts_by_date:
        return 0, 0

    # Find the longest run while checking that dates are truly consecutive.
    longest_streak = 0
    running_streak = 0
    previous_date: date | None = None

    for day_date in sorted(counts_by_date):
        if (
            counts_by_date[day_date] > 0
            and previous_date is not None
            and day_date == previous_date + timedelta(days=1)
        ):
            running_streak += 1
        elif counts_by_date[day_date] > 0:
            running_streak = 1
        else:
            running_streak = 0

        longest_streak = max(longest_streak, running_streak)
        previous_date = day_date

    # A streak may include today. If today is empty, preserve a streak ending
    # yesterday; an earlier streak is not considered current.
    streak_end = today if counts_by_date.get(today, 0) > 0 else today - timedelta(days=1)
    current_streak = 0

    while counts_by_date.get(streak_end, 0) > 0:
        current_streak += 1
        streak_end -= timedelta(days=1)

    return current_streak, longest_streak


def main() -> None:
    """Fetch the existing contribution data and print its streak results."""
    calendar = get_contribution_calendar()
    if calendar is None:
        sys.exit(1)

    current_streak, longest_streak = calculate_streaks(get_contribution_days(calendar))
    print(f"Current streak: {current_streak} days")
    print(f"Longest streak: {longest_streak} days")


if __name__ == "__main__":
    main()
