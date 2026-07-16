"""Statistics processing module for github-3d-contribution.

Parses raw GitHub data to calculate streaks (current, longest), aggregate repository
stargazers/forks, sum language bytes/percentages, and export compiled metrics to stats.json.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List

from src.utils import get_logger
import config

logger = get_logger("stats")


def calculate_streaks(days: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculates longest and current streaks from contribution calendar days.

    Args:
        days: Sorted list of day dictionaries from contribution calendar.

    Returns:
        Dictionary containing 'longest_streak' and 'current_streak'.
    """
    if not days:
        return {"current_streak": 0, "longest_streak": 0}

    # Ensure days are sorted by date
    sorted_days = sorted(days, key=lambda d: d["date"])

    # Calculate longest streak
    longest_streak = 0
    temp_streak = 0
    for day in sorted_days:
        if day["contributionCount"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate current streak timezone-independently
    # Uses the last day of the fetched calendar as the reference point
    calendar_last_date_str = sorted_days[-1]["date"]
    calendar_last_date = datetime.datetime.strptime(calendar_last_date_str, "%Y-%m-%d").date()

    last_contrib_idx = -1
    for i in range(len(sorted_days) - 1, -1, -1):
        if sorted_days[i]["contributionCount"] > 0:
            last_contrib_idx = i
            break

    current_streak = 0
    if last_contrib_idx != -1:
        last_contrib_date = datetime.datetime.strptime(
            sorted_days[last_contrib_idx]["date"], "%Y-%m-%d"
        ).date()
        
        # If the last contribution occurred on the last calendar day or the day prior
        if (calendar_last_date - last_contrib_date).days <= 1:
            for i in range(last_contrib_idx, -1, -1):
                if sorted_days[i]["contributionCount"] > 0:
                    current_streak += 1
                else:
                    # Streak broken
                    break

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }


def process_languages(repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates languages and computes percentages by byte size."""
    lang_bytes: Dict[str, int] = {}
    lang_colors: Dict[str, str] = {}

    for repo in repos:
        lang_edges = repo.get("languages", {}).get("edges", [])
        for edge in lang_edges:
            size = edge.get("size", 0)
            node = edge.get("node", {})
            name = node.get("name")
            color = node.get("color") or "#cccccc"
            
            if name:
                lang_bytes[name] = lang_bytes.get(name, 0) + size
                lang_colors[name] = color

    total_bytes = sum(lang_bytes.values())
    
    # Calculate percentages and sort
    sorted_langs = []
    if total_bytes > 0:
        for name, size in lang_bytes.items():
            pct = (size / total_bytes) * 100
            sorted_langs.append({
                "name": name,
                "bytes": size,
                "percentage": round(pct, 1),
                "color": lang_colors[name]
            })
        sorted_langs.sort(key=lambda l: l["bytes"], reverse=True)

    return {
        "total_bytes": total_bytes,
        "languages": sorted_langs
    }


def compile_stats() -> Dict[str, Any]:
    """Reads raw data, processes all statistics, and saves output/stats.json."""
    raw_file = config.DATA_DIR / "raw_data.json"
    stats_file = config.OUTPUT_DIR / "stats.json"

    if not raw_file.exists():
        logger.info(f"Raw data file not found at {raw_file}. Cascading to fetch contributions...")
        from src.fetch_contributions import fetch_all
        raw_data = fetch_all(config.USERNAME, config.GITHUB_TOKEN)
    else:
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

    graphql = raw_data["graphql"]
    lifetime = raw_data["lifetime"]
    is_mock = raw_data.get("is_mock", False)

    # Extract user profile information
    name = graphql.get("name") or graphql.get("login") or "GitHub User"
    login = graphql.get("login")
    followers = graphql.get("followers", {}).get("totalCount", 0)
    following = graphql.get("following", {}).get("totalCount", 0)

    # Parse repositories
    repos_nodes = graphql.get("repositories", {}).get("nodes", [])
    total_repos = graphql.get("repositories", {}).get("totalCount", 0)
    
    stars = sum(repo.get("stargazerCount", 0) for repo in repos_nodes)
    forks = sum(repo.get("forkCount", 0) for repo in repos_nodes)

    # Parse calendar and calculate streaks
    contrib_col = graphql.get("contributionsCollection", {})
    calendar = contrib_col.get("contributionCalendar", {})
    total_contributions = calendar.get("totalContributions", 0)
    
    # Flatten calendar weeks to days
    calendar_days = []
    weeks = calendar.get("weeks", [])
    for week in weeks:
        for day in week.get("contributionDays", []):
            calendar_days.append(day)

    streaks = calculate_streaks(calendar_days)
    lang_info = process_languages(repos_nodes)

    # Combine into a unified stats payload
    stats_payload = {
        "username": login,
        "display_name": name,
        "followers": followers,
        "following": following,
        "total_repositories": total_repos,
        "total_stars": stars,
        "total_forks": forks,
        "total_contributions": total_contributions,
        "current_streak": streaks["current_streak"],
        "longest_streak": streaks["longest_streak"],
        "lifetime_commits": lifetime.get("total_commits", 0),
        "lifetime_prs": lifetime.get("total_prs", 0),
        "lifetime_issues": lifetime.get("total_issues", 0),
        "lifetime_reviews": lifetime.get("total_reviews", 0),
        "languages": lang_info["languages"],
        "total_language_bytes": lang_info["total_bytes"],
        "is_mock_data": is_mock,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save to stats.json
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Statistics successfully written to: {stats_file}")
    return stats_payload


if __name__ == "__main__":
    compile_stats()
