"""Siddharth.dev - data-driven developer portfolio."""

import json
from pathlib import Path

from flask import Flask, abort, render_template


app = Flask(__name__)
app.config["SECRET_KEY"] = "siddharth-dev-portfolio"

PROJECTS_FILE = Path(__file__).resolve().parent / "data" / "projects.json"


def load_projects() -> list[dict]:
    """Load portfolio projects and assign display numbers dynamically."""
    with PROJECTS_FILE.open("r", encoding="utf-8") as file:
        projects = json.load(file)

    # Keep project numbering driven by the current list order.
    # Adding/removing/reordering projects never requires manually
    # fixing the visible numbers in projects.json.
    for index, project in enumerate(projects, start=1):
        project["number"] = f"{index:02d}"

    return projects


@app.route("/")
def index():
    """Render the project-first portfolio homepage."""
    return render_template("index.html", projects=load_projects())


@app.route("/info")
def info():
    """Render the portfolio information page."""
    return render_template("info.html")


@app.route("/project/<slug>")
def project_detail(slug: str):
    """Render a project case study from the project data file."""
    projects = load_projects()
    project = next((item for item in projects if item["slug"] == slug), None)
    if project is None:
        abort(404)

    # Only show a "Next project" link when another project actually exists.
    next_project = None
    if len(projects) > 1:
        current_index = projects.index(project)
        next_project = projects[(current_index + 1) % len(projects)]

    return render_template("project.html", project=project, next_project=next_project)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=False)
