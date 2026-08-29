"""Save verified practice solutions through GitHub's Contents API."""

import base64
import os
import re
import subprocess

import requests


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


def save_solution_to_github(token: str, owner: str, repository: str, path: str, source: str) -> dict:
    """Create one GitHub file commit, skipping unchanged source safely."""
    url = f"https://api.github.com/repos/{owner}/{repository}/contents/{path}"
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
    existing = requests.get(url, headers=headers, timeout=10)
    sha = None
    if existing.status_code == 200:
        existing_data = existing.json()
        existing_source = base64.b64decode(existing_data["content"]).decode("utf-8")
        if existing_source == source:
            return {"saved": False, "unchanged": True, "message": "This solution is already saved."}
        sha = existing_data["sha"]
    elif existing.status_code != 404:
        return {"saved": False, "unchanged": False, "message": "GitHub could not read the practice file."}
    payload = {"message": f"practice: solve {path.rsplit('/', 1)[-1].rsplit('.', 1)[0]}", "content": base64.b64encode(source.encode()).decode()}
    if sha:
        payload["sha"] = sha
    response = requests.put(url, headers=headers, json=payload, timeout=10)
    if response.status_code not in (200, 201):
        return {"saved": False, "unchanged": False, "message": "GitHub could not save the solution."}
    return {"saved": True, "unchanged": False, "message": "Solution saved to GitHub."}
