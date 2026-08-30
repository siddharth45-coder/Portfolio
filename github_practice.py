"""Save verified practice solutions through GitHub's Contents API."""

import base64
import os
import re
import subprocess

import requests
from dotenv import load_dotenv


# Keep this module independently usable; the token is never printed or sent to
# browser code. The local .env file remains Git-ignored.
load_dotenv()


def build_practice_path(problem: dict) -> str:
    """Build the repository path for a verified solution."""
    extension = {"Python": "py"}[problem["language"]]
    topic = re.sub(r"[^a-z0-9]+", "-", problem["topic"].lower()).strip("-")
    return f"practice/{problem['language'].lower()}/{topic}/{problem['id']}.{extension}"


def get_repository_name() -> str | None:
    """Read repository name from config or the local origin URL, never a token."""
    if os.getenv("GITHUB_REPOSITORY"):
        return os.getenv("GITHUB_REPOSITORY")
    try:
        remote = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    match = re.search(r"github\.com[/:]([^/]+/[^/]+?)(?:\.git)?$", remote)
    return match.group(1) if match else None


def get_repository_branch() -> str | None:
    """Read the target branch from config or the current local branch."""
    configured_branch = os.getenv("GITHUB_BRANCH")
    if configured_branch:
        return configured_branch
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    return branch or None


def save_solution_to_github(
    token: str, owner: str, repository: str, path: str, source: str,
    branch: str | None = None,
) -> dict:
    """Create one GitHub file commit, skipping unchanged source safely."""
    url = f"https://api.github.com/repos/{owner}/{repository}/contents/{path}"
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
    try:
        existing = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException:
        return {"saved": False, "unchanged": False, "message": "GitHub could not be reached while checking the practice file."}
    sha = None
    if existing.status_code == 200:
        existing_data = existing.json()
        existing_source = base64.b64decode(existing_data["content"]).decode("utf-8")
        if existing_source == source:
            return {"saved": False, "unchanged": True, "message": "This solution is already saved."}
        sha = existing_data["sha"]
    elif existing.status_code == 401:
        return {"saved": False, "unchanged": False, "message": "GitHub authentication failed. Check that GITHUB_TOKEN is valid."}
    elif existing.status_code == 403:
        return {"saved": False, "unchanged": False, "message": "GitHub denied repository access. Give GITHUB_TOKEN Contents read/write access to this repository."}
    elif existing.status_code != 404:
        return {"saved": False, "unchanged": False, "message": "GitHub could not read the practice file."}
    payload = {"message": f"practice: solve {path.rsplit('/', 1)[-1].rsplit('.', 1)[0]}", "content": base64.b64encode(source.encode()).decode()}
    if sha:
        payload["sha"] = sha
    if branch:
        payload["branch"] = branch
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=10)
    except requests.RequestException:
        return {"saved": False, "unchanged": False, "message": "GitHub could not be reached while saving the solution."}
    if response.status_code not in (200, 201):
        messages = {
            401: "GitHub authentication failed. Check that GITHUB_TOKEN is valid.",
            403: "GitHub denied the save. Give GITHUB_TOKEN Contents read/write access to this repository.",
            404: "GitHub could not find this repository or branch. Check origin and GITHUB_BRANCH.",
            409: "GitHub could not save because the repository branch changed. Please try the next submission.",
        }
        return {"saved": False, "unchanged": False, "message": messages.get(response.status_code, "GitHub could not save the solution.")}
    return {"saved": True, "unchanged": False, "message": "Solution saved to GitHub and committed to the configured branch."}
