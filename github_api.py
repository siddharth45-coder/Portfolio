"""Fetch basic profile information for the authenticated GitHub user."""

import os
import sys

import requests
from dotenv import load_dotenv


# Read variables from a local .env file. The file is listed in .gitignore.
load_dotenv()

# GitHub's endpoint for the currently authenticated user.
GITHUB_USER_URL = "https://api.github.com/user"


def get_github_profile() -> dict | None:
    """Request the authenticated user's profile, returning it on success."""
    # The token is never stored in this file; it comes from the environment.
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("Error: GITHUB_TOKEN is missing. Add it to your .env file.")
        return None

    # GitHub recommends sending the token in the Authorization header.
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        # A timeout prevents the program from waiting forever on network issues.
        response = requests.get(GITHUB_USER_URL, headers=headers, timeout=10)
    except requests.RequestException as error:
        print(f"Error: Could not reach the GitHub API: {error}")
        return None

    if response.status_code == 401:
        print("Error: The GitHub token is invalid or has expired.")
        return None

    if response.status_code != 200:
        print(f"Error: GitHub API request failed (status {response.status_code}).")
        return None

    return response.json()


def main() -> None:
    """Fetch and print the requested public profile fields."""
    profile = get_github_profile()
    if profile is None:
        sys.exit(1)

    print(f"GitHub username: {profile['login']}")
    print(f"GitHub name: {profile.get('name') or 'Not available'}")
    print(f"Public repositories: {profile['public_repos']}")


if __name__ == "__main__":
    main()
