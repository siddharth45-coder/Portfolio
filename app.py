"""A small Flask dashboard for the GitHub contribution and streak data."""

from flask import Flask, abort, render_template, request

from badges import calculate_badges
from contributions_api import get_contribution_calendar, get_contribution_days
from daily_goal import calculate_daily_goal
from github_api import get_github_profile
from leaderboard import rank_leaderboard
from problem_library import get_practice_summary, get_problem, list_problems
from streak_calculator import calculate_streaks
from streak_warning import calculate_streak_warning
from xp_calculator import calculate_xp_summary


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
    # There is currently no multi-user data source. Keep this empty rather
    # than inventing users; rank_leaderboard is ready for future real records.
    dashboard_data["leaderboard"] = rank_leaderboard([])
    return dashboard_data, None


@app.route("/")
def index():
    """Render the dashboard or an understandable error message."""
    dashboard_data, error = get_dashboard_data()
    return render_template("index.html", data=dashboard_data, error=error)


@app.route("/practice")
def practice():
    """Render the self-contained, storage-free practice problem library."""
    filters = {
        "search": request.args.get("search", ""),
        "difficulty": request.args.get("difficulty", ""),
        "topic": request.args.get("topic", ""),
        "status": request.args.get("status", ""),
    }
    return render_template(
        "practice.html", summary=get_practice_summary(),
        problems=list_problems(**filters), filters=filters,
        topics=sorted(get_practice_summary()["by_topic"]),
    )


@app.route("/practice/<problem_id>")
def practice_detail(problem_id: str):
    """Render a problem statement; editor and execution arrive in a later step."""
    problem = get_problem(problem_id)
    if problem is None:
        abort(404)
    return render_template("problem_detail.html", problem=problem)


if __name__ == "__main__":
    # debug=False prevents Flask from exposing extra development details.
    app.run(debug=False)
