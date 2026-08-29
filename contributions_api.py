"""Fetch the authenticated GitHub user's contribution calendar for this year."""

import os
import sys
from datetime import date

import requests
from dotenv import load_dotenv


# Read the token from the local, Git-ignored .env file.
load_dotenv()

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

# This query asks for one count and one date for every calendar day.
CONTRIBUTIONS_QUERY = """
query ContributionCalendar($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def get_current_year_dates() -> tuple[str, str]:
    """Return GitHub GraphQL date-time values from January 1 through today."""
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    return (
        f"{start_of_year.isoformat()}T00:00:00Z",
        f"{today.isoformat()}T23:59:59Z",
    )


def get_contribution_calendar() -> dict | None:
    """Request this year's contribution calendar from GitHub GraphQL."""
    # The token stays in the environment and is never printed.
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN is missing. Add it to your .env file.")
        return None

    from_date, to_date = get_current_year_dates()
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "query": CONTRIBUTIONS_QUERY,
        "variables": {"from": from_date, "to": to_date},
    }

    try:
        response = requests.post(
            GITHUB_GRAPHQL_URL, headers=headers, json=payload, timeout=10
        )
    except requests.RequestException as error:
        print(f"Error: Could not reach the GitHub API: {error}")
        return None

    if response.status_code == 401:
        print("Error: The GitHub token is invalid or has expired.")
        return None

    if response.status_code != 200:
        print(f"Error: GitHub API request failed (status {response.status_code}).")
        return None

    try:
        response_data = response.json()
    except requests.JSONDecodeError:
        print("Error: GitHub returned an unreadable response.")
        return None

    # GraphQL can return errors with an HTTP 200 status, so check explicitly.
    if response_data.get("errors"):
        error_messages = "; ".join(
            error.get("message", "Unknown GraphQL error")
            for error in response_data["errors"]
        )
        if "credential" in error_messages.lower() or "token" in error_messages.lower():
            print("Error: The GitHub token is invalid or lacks required access.")
        else:
            print(f"Error: GitHub GraphQL request failed: {error_messages}")
        return None

    calendar = (
        response_data.get("data", {})
        .get("viewer", {})
        .get("contributionsCollection", {})
        .get("contributionCalendar")
    )
    if not calendar:
        print("Error: GitHub did not return contribution calendar data.")
        return None

    return calendar


def get_contribution_days(calendar: dict) -> list[dict]:
    """Flatten GitHub's calendar weeks into a simple list of daily records."""
    return [
        day
        for week in calendar.get("weeks", [])
        for day in week.get("contributionDays", [])
    ]


def main() -> None:
    """Print one date and contribution count for each day in the current year."""
    calendar = get_contribution_calendar()
    if calendar is None:
        sys.exit(1)

    current_year = str(date.today().year)
    days = [
        day for day in get_contribution_days(calendar) if day.get("date", "").startswith(current_year)
    ]

    if not days:
        print("Error: GitHub returned no contribution days for the current year.")
        sys.exit(1)

    for day in days:
        print(f"{day['date']}: {day['contributionCount']} contributions")

    print(f"Total contributions: {calendar['totalContributions']}")


if __name__ == "__main__":
    main()
