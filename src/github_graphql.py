"""GitHub GraphQL API client wrapper for github-3d-contribution.

Handles the construct and execution of GraphQL queries, authenticates
requests, and manages API errors.
"""

from typing import Dict, Any, Optional
from src.utils import get_http_session, get_logger
import config

logger = get_logger("github-graphql")

# The main GraphQL query to fetch the user statistics, repos, languages,
# and contribution calendar
GRAPHQL_QUERY = """
query($username: String!) {
  user(login: $username) {
    name
    login
    createdAt
    followers {
      totalCount
    }
    following {
      totalCount
    }
    repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: CREATED_AT, direction: DESC}) {
      totalCount
      nodes {
        name
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
            weekday
          }
        }
      }
    }
  }
}
"""


def execute_query(
    username: str,
    token: Optional[str]
) -> Dict[str, Any]:
    """Executes the GraphQL query to fetch user data from GitHub.

    Args:
        username: The target GitHub username.
        token: The Personal Access Token for authentication.

    Returns:
        The response dictionary from the GitHub GraphQL API.

    Raises:
        ValueError: If GITHUB_TOKEN is not supplied and mock is disabled.
        RuntimeError: If the HTTP request fails or the GraphQL query returns errors.
    """
    if not token:
        logger.warning(
            "GITHUB_TOKEN is missing. Cannot call the live GitHub API."
        )
        raise ValueError("GitHub Token is required for live GraphQL calls.")

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "github-3d-contribution-agent"
    }
    payload = {
        "query": GRAPHQL_QUERY,
        "variables": {"username": username}
    }

    session = get_http_session()
    try:
        logger.info(f"Executing GraphQL query for username: {username}...")
        response = session.post(url, json=payload, headers=headers, timeout=20)
        
        # Check HTTP level status
        response.raise_for_status()
        
        result = response.json()
        
        # Check GraphQL level errors
        if "errors" in result:
            errors = result["errors"]
            err_msg = "; ".join([e.get("message", "Unknown error") for e in errors])
            logger.error(f"GraphQL errors returned: {err_msg}")
            raise RuntimeError(f"GitHub GraphQL query errors: {err_msg}")
            
        if "data" not in result or not result["data"] or "user" not in result["data"]:
            logger.error(f"GraphQL returned empty data. Response: {result}")
            raise RuntimeError("GitHub GraphQL query returned no user data.")

        return result["data"]

    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code if http_err.response else "Unknown"
        logger.error(f"HTTP error during GraphQL execution (status {status_code}): {http_err}")
        if status_code == 401:
            logger.error("Authentication failed. Please verify that your GITHUB_TOKEN is valid.")
        raise RuntimeError(f"HTTP call to GitHub GraphQL failed: {http_err}")
    except Exception as exc:
        logger.error(f"Failed to execute GraphQL query: {exc}")
        raise RuntimeError(f"Failed to execute GraphQL query: {exc}")
