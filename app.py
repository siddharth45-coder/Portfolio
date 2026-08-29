"""A small Flask dashboard for the GitHub contribution and streak data."""

from flask import Flask, render_template

from contributions_api import get_contribution_calendar, get_contribution_days
from github_api import get_github_profile
from streak_calculator import calculate_streaks


app = Flask(__name__)


def get_dashboard_data() -> tuple[dict | None, str | None]:
    """Collect the existing GitHub data needed by the dashboard."""
    # These functions already read the token from .env and handle API errors.
    profile = get_github_profile()
    if profile is None:
        return None, "Unable to load your GitHub profile. Check your token and connection."

    calendar = get_contribution_calendar()
    if calendar is None:
        return None, "Unable to load contribution data. Check your token and connection."

    current_streak, longest_streak = calculate_streaks(get_contribution_days(calendar))
    dashboard_data = {
        "username": profile.get("login", "GitHub user"),
        "total_contributions": calendar.get("totalContributions", 0),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }
    return dashboard_data, None


@app.route("/")
def index():
    """Render the dashboard or an understandable error message."""
    dashboard_data, error = get_dashboard_data()
    return render_template("index.html", data=dashboard_data, error=error)


if __name__ == "__main__":
    # debug=False prevents Flask from exposing extra development details.
    app.run(debug=False)
