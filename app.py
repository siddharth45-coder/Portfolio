"""A small Flask dashboard for the GitHub contribution and streak data."""

import os

from flask import Flask, abort, render_template, request, session

from badges import calculate_badges
from contributions_api import get_contribution_calendar, get_contribution_days
from daily_goal import calculate_daily_goal
from github_api import get_github_profile
from leaderboard import rank_leaderboard
from github_practice import build_practice_path, get_repository_name, save_solution_to_github
from problem_library import PROBLEMS, get_practice_summary, get_problem, list_problems
from practice_evaluator import evaluate_solution
from practice_rewards import award_practice_xp, calculate_practice_xp
from streak_calculator import calculate_streaks
from streak_warning import calculate_streak_warning
from xp_calculator import calculate_xp_summary


app = Flask(__name__)
# Set FLASK_SECRET_KEY in production. This development fallback only signs the
# session that stores solved practice IDs; it is not a GitHub credential.
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "codestreak-development-session-key")


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
    solved_ids = set(session.get("solved_problem_ids", []))
    problems = [dict(problem, is_solved=problem["id"] in solved_ids) for problem in list_problems(**filters)]
    summary = get_practice_summary()
    summary["solved"] = len(solved_ids)
    summary["unsolved"] = summary["total"] - summary["solved"]
    summary["completion_percent"] = round(summary["solved"] / summary["total"] * 100) if summary["total"] else 0
    return render_template(
        "practice.html", summary=summary,
        problems=problems, filters=filters,
        topics=sorted(get_practice_summary()["by_topic"]),
        practice_xp=calculate_practice_xp(session.get("rewarded_problem_ids", []), list(PROBLEMS)),
    )


@app.route("/practice/<problem_id>")
def practice_detail(problem_id: str):
    """Render a problem statement; editor and execution arrive in a later step."""
    problem = get_problem(problem_id, include_tests=True)
    if problem is None:
        abort(404)
    problem["is_solved"] = problem_id in session.get("solved_problem_ids", [])
    return render_template("problem_detail.html", problem=problem, code=problem["starter_code"], result=None, message=None)


@app.post("/practice/<problem_id>/evaluate")
def practice_evaluate(problem_id: str):
    """Run public tests or submit all tests in a child process."""
    problem = get_problem(problem_id, include_tests=True)
    if problem is None:
        abort(404)
    source = request.form.get("code", "")
    is_submission = request.form.get("action") == "submit"
    result = evaluate_solution(problem, source, include_hidden=is_submission)
    message = None
    if is_submission and result["is_solved"]:
        solved_ids = session.get("solved_problem_ids", [])
        if problem_id not in solved_ids:
            solved_ids.append(problem_id)
            session["solved_problem_ids"] = solved_ids
        reward = award_practice_xp(session.get("rewarded_problem_ids", []), problem_id, problem["difficulty"])
        session["rewarded_problem_ids"] = reward["rewarded_problem_ids"]
        message = f"Solved! You earned {reward['awarded_xp']} practice XP." if reward["awarded_xp"] else "Solved! Practice XP was already awarded."
    problem["is_solved"] = problem_id in session.get("solved_problem_ids", [])
    return render_template("problem_detail.html", problem=problem, code=source, result=result, message=message)


@app.post("/practice/<problem_id>/save")
def practice_save(problem_id: str):
    """Save a verified solution to the authenticated user's GitHub repository."""
    problem = get_problem(problem_id, include_tests=True)
    if problem is None:
        abort(404)
    source = request.form.get("code", "")
    message = "Solve all required tests before saving this solution."
    if problem_id in session.get("solved_problem_ids", []):
        profile = get_github_profile()
        token = os.getenv("GITHUB_TOKEN")
        repository = get_repository_name()
        if profile and token and repository and "/" in repository:
            owner, repository_name = repository.split("/", 1)
            # Remote ownership is authoritative; never send the token to HTML.
            save_result = save_solution_to_github(token, owner, repository_name, build_practice_path(problem), source)
            message = save_result["message"]
        else:
            message = "GitHub repository configuration is unavailable."
    problem["is_solved"] = problem_id in session.get("solved_problem_ids", [])
    return render_template("problem_detail.html", problem=problem, code=source, result=None, message=message)


if __name__ == "__main__":
    # debug=False prevents Flask from exposing extra development details.
    app.run(debug=False)
