"""CodeStreak GitHub activity dashboard."""

import os

from flask import Flask, render_template

from badges import calculate_badges
from contributions_api import get_contribution_calendar, get_contribution_days
from daily_goal import calculate_daily_goal
from github_api import get_github_profile
from leaderboard import rank_leaderboard
from streak_calculator import calculate_streaks
from streak_warning import calculate_streak_warning
from xp_calculator import calculate_xp_summary


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "codestreak-development-session-key")


def get_dashboard_data() -> tuple[dict | None, str | None]:
    """Collect the GitHub activity data used by the dashboard only."""
    profile = get_github_profile()
    if profile is None:
        return None, "Unable to load your GitHub profile. Check your token and connection."

    calendar = get_contribution_calendar()
    if calendar is None:
        return None, "Unable to load contribution data. Check your token and connection."

    contribution_days = get_contribution_days(calendar)
    current_streak, longest_streak = calculate_streaks(contribution_days)
    xp_data = calculate_xp_summary(contribution_days, current_streak)

    dashboard_data = {
        "username": profile.get("login", "GitHub user"),
        "total_contributions": calendar.get("totalContributions", 0),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        **xp_data,
    }
    dashboard_data["badges"] = calculate_badges(
        dashboard_data["total_contributions"], longest_streak, xp_data["level"]
    )
    dashboard_data["daily_goal"] = calculate_daily_goal(contribution_days)
    dashboard_data["streak_warning"] = calculate_streak_warning(
        contribution_days, current_streak
    )
    dashboard_data["leaderboard"] = rank_leaderboard([])
    return dashboard_data, None


@app.route("/")
def index():
    """Render the GitHub activity dashboard."""
    dashboard_data, error = get_dashboard_data()
    return render_template("index.html", data=dashboard_data, error=error)


if __name__ == "__main__":
    app.run(debug=False)
