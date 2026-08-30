"""A small Flask dashboard for the GitHub contribution and streak data."""

import os

from flask import Flask, abort, render_template, request, session

from badges import calculate_badges
from contributions_api import get_contribution_calendar, get_contribution_days
from daily_challenge import get_daily_challenge
from daily_goal import calculate_daily_goal
from github_api import get_github_profile
from leaderboard import rank_leaderboard
from github_practice import build_practice_path, get_repository_branch, get_repository_name, save_solution_to_github
from problem_library import PROBLEMS, get_problem, list_problems
from practice_evaluator import evaluate_solution
from practice_analytics import TOPIC_DEFINITIONS, calculate_practice_statistics, calculate_topic_progress
from practice_analytics import calculate_advanced_analytics
from practice_preferences import DEFAULT_PREFERENCES, normalize_preferences
from recommendations import recommend_problems
from practice_rewards import award_practice_xp
from submission_history import record_submission
from milestones import calculate_milestones
from streak_calculator import calculate_streaks
from streak_warning import calculate_streak_warning
from xp_calculator import calculate_xp_summary
from weekly_challenge import get_weekly_challenge


app = Flask(__name__)
# Set FLASK_SECRET_KEY in production. This development fallback only signs the
# session that stores solved practice IDs; it is not a GitHub credential.
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "codestreak-development-session-key")


def get_practice_data() -> dict:
    """Build all session-scoped practice data in one place for practice pages."""
    solved_ids = set(session.get("solved_problem_ids", []))
    rewarded_ids = session.get("rewarded_problem_ids", [])
    submissions = session.get("submission_history", [])
    preferences = normalize_preferences(session.get("practice_preferences", DEFAULT_PREFERENCES))
    statistics = calculate_practice_statistics(PROBLEMS, solved_ids, rewarded_ids, submissions)
    topic_progress = calculate_topic_progress(PROBLEMS, solved_ids)
    weekly_challenge = get_weekly_challenge(PROBLEMS, solved_ids)
    return {
        "solved_ids": solved_ids,
        "rewarded_ids": rewarded_ids,
        "submissions": submissions,
        "statistics": statistics, "preferences": preferences,
        "topic_progress": topic_progress,
        "daily_challenge": get_daily_challenge(PROBLEMS, solved_ids),
        "weekly_challenge": weekly_challenge,
        "recommendations": recommend_problems(PROBLEMS, solved_ids, preferences, submissions),
        "milestones": calculate_milestones(statistics, topic_progress, weekly_challenge),
        "advanced_analytics": calculate_advanced_analytics(statistics, submissions),
    }


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
    practice_data = get_practice_data()
    # Solved state belongs to the signed browser session, not static library data.
    library_filters = dict(filters, status="")
    problems = [dict(problem, is_solved=problem["id"] in practice_data["solved_ids"]) for problem in list_problems(**library_filters)]
    if filters["status"] == "solved":
        problems = [problem for problem in problems if problem["is_solved"]]
    elif filters["status"] == "unsolved":
        problems = [problem for problem in problems if not problem["is_solved"]]
    return render_template(
        "practice.html", summary=practice_data["statistics"],
        problems=problems, filters=filters,
        topics=TOPIC_DEFINITIONS,
        daily_challenge=practice_data["daily_challenge"],
        topic_progress=practice_data["topic_progress"],
        submissions=practice_data["submissions"],
        preferences=practice_data["preferences"],
        weekly_challenge=practice_data["weekly_challenge"],
        recommendations=practice_data["recommendations"],
        milestones=practice_data["milestones"],
        advanced_analytics=practice_data["advanced_analytics"],
    )


@app.route("/coding-lab")
@app.route("/coding-lab/<problem_id>")
def coding_lab(problem_id: str | None = None):
    """Render the Three.js coding lab around an existing practice problem."""
    problem = get_problem(problem_id or PROBLEMS[0]["id"], include_tests=True)
    if problem is None:
        abort(404)
    problem["is_solved"] = problem["id"] in session.get("solved_problem_ids", [])
    return render_lab(problem, problem["starter_code"], None)


def render_lab(problem: dict, code: str, result: dict | None, message: str | None = None):
    """Render the lab consistently without sending secrets to the browser."""
    return render_template(
        "coding_lab.html", problem=problem, problems=PROBLEMS, code=code,
        result=result, message=message,
        lab_history=session.get("coding_lab_history", [])[:5],
    )


@app.post("/coding-lab/<problem_id>/run")
def coding_lab_run(problem_id: str):
    """Run public tests through the established Phase 3 evaluator."""
    problem = get_problem(problem_id, include_tests=True)
    if problem is None:
        abort(404)
    source = request.form.get("code", "")
    result = evaluate_solution(problem, source, include_hidden=False)
    problem["is_solved"] = problem_id in session.get("solved_problem_ids", [])
    return render_lab(problem, source, result)


@app.post("/coding-lab/<problem_id>/submit")
def coding_lab_submit(problem_id: str):
    """Submit with hidden tests, existing XP, history, and token-safe GitHub save."""
    problem = get_problem(problem_id, include_tests=True)
    if problem is None:
        abort(404)
    source = request.form.get("code", "")
    result = evaluate_solution(problem, source, include_hidden=True)
    if not result["is_solved"]:
        history = record_submission(session.get("submission_history", []), problem, result)
        session["submission_history"] = history
        session["coding_lab_history"] = history
        problem["is_solved"] = problem_id in session.get("solved_problem_ids", [])
        return render_lab(problem, source, result, "Submission failed. Fix the tests before submitting again.")

    submitted_ids = session.get("coding_lab_submitted_ids", [])
    if problem_id in submitted_ids:
        problem["is_solved"] = True
        return render_lab(problem, source, result, "This solution was already submitted safely; no duplicate XP or GitHub commit was created.")

    solved_ids = session.get("solved_problem_ids", [])
    if problem_id not in solved_ids:
        solved_ids.append(problem_id)
        session["solved_problem_ids"] = solved_ids
    reward = award_practice_xp(session.get("rewarded_problem_ids", []), problem_id, problem["difficulty"])
    session["rewarded_problem_ids"] = reward["rewarded_problem_ids"]

    github_status = "GitHub save unavailable. Your local session submission remains successful."
    token = os.getenv("GITHUB_TOKEN")
    repository = get_repository_name()
    branch = get_repository_branch()
    # The token is only used server-side by the existing Contents API helper.
    if not token:
        github_status = "GitHub save skipped: GITHUB_TOKEN is missing from the local environment."
    elif not repository or "/" not in repository:
        github_status = "GitHub save skipped: the origin repository is not configured."
    elif not branch:
        github_status = "GitHub save skipped: the target branch could not be determined."
    elif not get_github_profile():
        github_status = "GitHub save skipped: token authentication could not be verified."
    else:
        owner, repository_name = repository.split("/", 1)
        save_result = save_solution_to_github(
            token, owner, repository_name, build_practice_path(problem), source, branch
        )
        github_status = save_result["message"]

    submitted_ids.append(problem_id)
    session["coding_lab_submitted_ids"] = submitted_ids
    history = record_submission(
        session.get("submission_history", []), problem, result,
        xp_earned=reward["awarded_xp"], github_status=github_status,
    )
    session["submission_history"] = history
    session["coding_lab_history"] = history
    problem["is_solved"] = True
    message = f"Solution submitted. You earned {reward['awarded_xp']} practice XP. {github_status}"
    return render_lab(problem, source, result, message)


@app.post("/practice/preferences")
def practice_preferences():
    """Store only supported, non-secret preferences in the signed session."""
    session["practice_preferences"] = normalize_preferences({
        "language": request.form.get("language"),
        "topics": request.form.getlist("topics"),
        "difficulty": request.form.get("difficulty"),
        "weekly_goal": request.form.get("weekly_goal"),
    })
    return practice()


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
    # Keep every Run/Submit attempt in session history, with no source or hidden data.
    session["submission_history"] = record_submission(
        session.get("submission_history", []), problem, result
    )
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
