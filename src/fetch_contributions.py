"""Fetch contributions module for github-3d-contribution.

Retrieves details from GitHub's GraphQL and REST Search APIs, compiling
them into a raw JSON file. Supports a comprehensive offline simulation mode.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import math
import random
import datetime
from typing import Dict, Any, Optional

from src.utils import get_http_session, get_logger
from src.github_graphql import execute_query
import config

logger = get_logger("fetch-contributions")


def generate_mock_data(username: str) -> Dict[str, Any]:
    """Generates highly realistic simulated GitHub data for offline testing."""
    logger.info("Generating realistic mock data for offline dashboard generation...")
    
    # Align starting date to 365 days ago, snapped to Sunday
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=365)
    start_date = start_date - datetime.timedelta(days=(start_date.weekday() + 1) % 7)
    
    random.seed(username)  # Stable mock data per username
    
    days = []
    current_date = start_date
    total_contribs = 0
    
    while current_date <= today:
        weekday = (current_date.weekday() + 1) % 7  # 0 = Sunday, 1 = Monday
        is_weekend = weekday in (0, 6)
        
        # Base probability of contribution
        base_prob = 0.15 if is_weekend else 0.6
        # Sine wave to simulate busy and quiet months
        wave = math.sin((current_date - start_date).days / 20.0) * 0.35 + 0.65
        prob = base_prob * wave
        
        if random.random() < prob:
            count = random.choice([1, 1, 1, 2, 2, 3, 4, 5, 8, 14])
        else:
            count = 0
            
        total_contribs += count
        
        # Assign levels matching GitHub limits
        if count == 0:
            level = "NONE"
        elif count <= 2:
            level = "FIRST_QUARTILE"
        elif count <= 4:
            level = "SECOND_QUARTILE"
        elif count <= 7:
            level = "THIRD_QUARTILE"
        else:
            level = "FOURTH_QUARTILE"
            
        days.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "contributionCount": count,
            "contributionLevel": level,
            "weekday": weekday
        })
        current_date += datetime.timedelta(days=1)
        
    # Group days into weeks
    weeks = []
    for i in range(0, len(days), 7):
        week_days = days[i:i+7]
        if week_days:
            weeks.append({"contributionDays": week_days})
            
    # Mock repositories and languages
    languages_mock = [
        {"node": {"name": "Python", "color": "#3572A5"}, "size": 350000},
        {"node": {"name": "TypeScript", "color": "#3178c6"}, "size": 220000},
        {"node": {"name": "Go", "color": "#00ADD8"}, "size": 110000},
        {"node": {"name": "HTML", "color": "#e34c26"}, "size": 40000},
        {"node": {"name": "CSS", "color": "#563d7c"}, "size": 30000},
    ]
    
    mock_repos = [
        {"name": "auto-visualizer", "stargazerCount": 42, "forkCount": 8, "languages": {"edges": languages_mock[:3]}},
        {"name": "fast-api-service", "stargazerCount": 28, "forkCount": 4, "languages": {"edges": [languages_mock[0], languages_mock[3]]}},
        {"name": "portfolio-site", "stargazerCount": 15, "forkCount": 2, "languages": {"edges": languages_mock[2:]}},
        {"name": "python-scripts", "stargazerCount": 8, "forkCount": 1, "languages": {"edges": [languages_mock[0]]}}
    ]

    mock_profile = {
        "name": f"Mock Developer ({username})",
        "login": username,
        "createdAt": "2020-01-15T00:00:00Z",
        "followers": {"totalCount": 87},
        "following": {"totalCount": 43},
        "repositories": {
            "totalCount": len(mock_repos),
            "nodes": mock_repos
        },
        "contributionsCollection": {
            "totalCommitContributions": int(total_contribs * 0.7),
            "totalIssueContributions": int(total_contribs * 0.1),
            "totalPullRequestContributions": int(total_contribs * 0.15),
            "totalPullRequestReviewContributions": int(total_contribs * 0.05),
            "contributionCalendar": {
                "totalContributions": total_contribs,
                "weeks": weeks
            }
        }
    }
    
    # Compile final data structure
    return {
        "graphql": mock_profile,
        "lifetime": {
            "total_commits": int(total_contribs * 1.5) + 300,
            "total_prs": int(total_contribs * 0.3) + 40,
            "total_issues": int(total_contribs * 0.25) + 20,
            "total_reviews": int(total_contribs * 0.1) + 10,
        },
        "is_mock": True
    }


def fetch_lifetime_stats(username: str, token: str) -> Dict[str, int]:
    """Fetches lifetime statistics using GitHub REST Search APIs.

    If rates are limited or queries fail, falls back to default values.
    """
    logger.info(f"Fetching lifetime stats for {username}...")
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "github-3d-contribution-agent",
        "Accept": "application/vnd.github.v3+json"
    }
    
    session = get_http_session()
    stats = {
        "total_commits": 0,
        "total_prs": 0,
        "total_issues": 0,
        "total_reviews": 0
    }
    
    # 1. Fetch total commits (Uses specialized Accept header for cloak preview)
    commit_headers = headers.copy()
    commit_headers["Accept"] = "application/vnd.github.cloak-preview+json"
    try:
        commit_url = f"https://api.github.com/search/commits?q=author:{username}"
        res = session.get(commit_url, headers=commit_headers, timeout=15)
        if res.status_code == 200:
            stats["total_commits"] = res.json().get("total_count", 0)
        else:
            logger.warning(f"Commits search API returned status {res.status_code}")
    except Exception as e:
        logger.warning(f"Could not retrieve lifetime commits: {e}")

    # 2. Fetch total PRs
    try:
        prs_url = f"https://api.github.com/search/issues?q=author:{username}+type:pr"
        res = session.get(prs_url, headers=headers, timeout=15)
        if res.status_code == 200:
            stats["total_prs"] = res.json().get("total_count", 0)
    except Exception as e:
        logger.warning(f"Could not retrieve lifetime PRs: {e}")

    # 3. Fetch total issues
    try:
        issues_url = f"https://api.github.com/search/issues?q=author:{username}+type:issue"
        res = session.get(issues_url, headers=headers, timeout=15)
        if res.status_code == 200:
            stats["total_issues"] = res.json().get("total_count", 0)
    except Exception as e:
        logger.warning(f"Could not retrieve lifetime Issues: {e}")

    # 4. Fetch PR reviews
    try:
        # Reviews can be queried by search queries for PRs reviewed by user
        reviews_url = f"https://api.github.com/search/issues?q=reviewed-by:{username}+type:pr"
        res = session.get(reviews_url, headers=headers, timeout=15)
        if res.status_code == 200:
            stats["total_reviews"] = res.json().get("total_count", 0)
    except Exception as e:
        logger.warning(f"Could not retrieve reviews: {e}")

    return stats


def fetch_all(username: str, token: Optional[str] = None) -> Dict[str, Any]:
    """Fetches all repository and contribution stats, saving to data/raw_data.json."""
    data_file = config.DATA_DIR / "raw_data.json"
    
    # Check if we should use live API or mock fallback
    if not token:
        logger.warning("No authentication token provided. Using mock data mode.")
        raw_data = generate_mock_data(username)
    else:
        try:
            graphql_data = execute_query(username, token)
            lifetime_stats = fetch_lifetime_stats(username, token)
            
            raw_data = {
                "graphql": graphql_data,
                "lifetime": lifetime_stats,
                "is_mock": False
            }
            logger.info("Successfully fetched all stats from live GitHub APIs.")
        except Exception as exc:
            logger.error(
                f"Failed to fetch from live APIs: {exc}. "
                "Falling back to mock data so dashboard generation can continue."
            )
            raw_data = generate_mock_data(username)

    # Save to data directory
    try:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Raw data saved to {data_file}")
    except Exception as e:
        logger.error(f"Failed to save raw data file: {e}")

    return raw_data


if __name__ == "__main__":
    # Fetch data directly when executing script
    fetch_all(config.USERNAME, config.GITHUB_TOKEN)
