"""README updater module for github-3d-contribution.

Reads compiled stats from stats.json, builds a clean HTML/Markdown representation,
and inserts it into README.md between specific section tags. Overwrites README.md
with a complete showcase page if markers do not exist.
"""

import re
import json
import datetime
from pathlib import Path
from typing import Dict, Any

from src.utils import get_logger
import config

logger = get_logger("update-readme")

START_TAG = "<!-- START_SECTION:dashboard -->"
END_TAG = "<!-- END_SECTION:dashboard -->"


def format_number(val: int) -> str:
    """Formats integers with thousands separators."""
    return f"{val:,}"


def build_dashboard_html(stats: Dict[str, Any]) -> str:
    """Compiles the HTML dashboard block to be embedded in the README."""
    username = stats["username"]
    display_name = stats.get("display_name", username)
    total_contribs = format_number(stats.get("total_contributions", 0))
    current_streak = format_number(stats.get("current_streak", 0))
    longest_streak = format_number(stats.get("longest_streak", 0))
    stars = format_number(stats.get("total_stars", 0))
    forks = format_number(stats.get("total_forks", 0))
    repos = format_number(stats.get("total_repositories", 0))
    commits = format_number(stats.get("lifetime_commits", 0))
    prs = format_number(stats.get("lifetime_prs", 0))
    issues = format_number(stats.get("lifetime_issues", 0))
    reviews = format_number(stats.get("lifetime_reviews", 0))
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_mock_notice = ""
    if stats.get("is_mock_data", False):
        is_mock_notice = '\n<p align="center">⚠️ <i>Note: Displaying mock data for demonstration. Set GITHUB_TOKEN to show live stats.</i></p>\n'

    # Build the HTML content block
    html = f"""{START_TAG}
<div align="center">
  {is_mock_notice}
  <!-- 3D Contribution Graph -->
  <a href="https://github.com/{username}">
    <img src="output/contribution-3d.svg" alt="{display_name}'s 3D GitHub Contribution Calendar" width="840" style="max-width: 100%;" />
  </a>
  <br/><br/>
  
  <!-- Radar Chart and Language Donut Chart Side-by-Side -->
  <table border="0" cellpadding="0" cellspacing="0" align="center" style="border-collapse: collapse; border: none; margin: 0 auto;">
    <tr style="border: none;">
      <td valign="top" style="border: none; padding: 0 10px;">
        <img src="output/radar.svg" alt="Developer Stats Radar" width="410" style="max-width: 100%;" />
      </td>
      <td valign="top" style="border: none; padding: 0 10px;">
        <img src="output/language-donut.svg" alt="Language Donut Chart" width="410" style="max-width: 100%;" />
      </td>
    </tr>
  </table>
  <br/>

  <!-- Statistics Summary Table -->
  <h3>🚀 Profile Metrics Showcase</h3>
  
  <table align="center" style="width: 80%; border-collapse: collapse;">
    <thead>
      <tr style="background-color: #161b22; border-bottom: 2px solid #30363d;">
        <th align="left" style="padding: 8px; border: 1px solid #30363d;">🏆 Metric</th>
        <th align="center" style="padding: 8px; border: 1px solid #30363d;">Count</th>
        <th align="left" style="padding: 8px; border: 1px solid #30363d;">🔥 Metric</th>
        <th align="center" style="padding: 8px; border: 1px solid #30363d;">Count</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding: 8px; border: 1px solid #30363d;">Year Contributions</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{total_contribs}</b></td>
        <td style="padding: 8px; border: 1px solid #30363d;">Current Streak</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{current_streak} days</b></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #30363d;">Lifetime Commits</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{commits}</b></td>
        <td style="padding: 8px; border: 1px solid #30363d;">Longest Streak</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{longest_streak} days</b></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #30363d;">Total Stars Received</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{stars}</b></td>
        <td style="padding: 8px; border: 1px solid #30363d;">Total Forks Created</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{forks}</b></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #30363d;">Owned Repositories</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{repos}</b></td>
        <td style="padding: 8px; border: 1px solid #30363d;">Pull Request Reviews</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{reviews}</b></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #30363d;">Pull Requests Created</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{prs}</b></td>
        <td style="padding: 8px; border: 1px solid #30363d;">Issues Created</td>
        <td align="center" style="padding: 8px; border: 1px solid #30363d;"><b>{issues}</b></td>
      </tr>
    </tbody>
  </table>
  <br/>

  <p align="center">
    <sub>Last Generated: <b>{timestamp}</b> | Built with <a href="https://github.com/Abad-87/github-3d-contribution">github-3d-contribution</a></sub>
  </p>
</div>
{END_TAG}"""
    return html


def get_default_readme(dashboard_html: str) -> str:
    """Creates a beautiful standard default README if one needs to be initialized."""
    return f"""# 📊 GitHub 3D Contribution Dashboard

<p align="center">
  <a href="https://github.com/{config.USERNAME}/github-3d-contribution/actions/workflows/update.yml">
    <img src="https://github.com/{config.USERNAME}/github-3d-contribution/actions/workflows/update.yml/badge.svg" alt="Workflow Build Status" />
  </a>
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python Version" />
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
  </a>
</p>

Automatically generate beautiful 3D isometric calendars, language donut slices, and developer profile radar charts for your GitHub Profile README.

---

{dashboard_html}

---

## 🛠️ How It Works
The script fetches your contribution matrix via **GitHub GraphQL API** and REST Search API, calculates streaks, sorts languages, projects coordinates into a 3D isometric space, generates three standalone vector SVGs (plus PNG conversions), and writes them directly into the output directory and updates this README.

## 🚀 Local Run
1. Clone the repository:
   ```bash
   git clone https://github.com/Abad-87/github-3d-contribution.git
   cd github-3d-contribution
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your token (create a `.env` file or export it):
   ```env
   GH_TOKEN=your_personal_access_token
   GITHUB_USERNAME=your_username
   THEME=dark
   PALETTE=purple
   ```
4. Execute the collection and generation chain:
   ```bash
   # Fetch stats
   python src/fetch_contributions.py
   # Compile statistics
   python src/stats.py
   # Render isometric graph
   python src/generate_3d.py
   # Render donut chart
   python src/generate_donut.py
   # Render radar chart
   python src/generate_radar.py
   # Write to README
   python src/update_readme.py
   ```

## ⚙️ GitHub Actions Automation
Configure this updater to run daily on your profile repository by copying the workflow file located in `.github/workflows/update.yml`.

## 📄 License
This repository is open-source and licensed under the [MIT License](LICENSE).
"""


def update_readme() -> None:
    """Updates the project README.md file with the compiled HTML dashboard."""
    stats_file = config.OUTPUT_DIR / "stats.json"
    readme_file = config.BASE_DIR / "README.md"
    
    if not stats_file.exists():
        logger.info(f"Stats file not found at {stats_file}. Cascading to stats compilation...")
        from src.stats import compile_stats
        stats = compile_stats()
    else:
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

    # Build the HTML insert block
    dashboard_html = build_dashboard_html(stats)
    
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Match using regex between the START and END tags
        pattern = re.compile(
            rf"{re.escape(START_TAG)}.*?{re.escape(END_TAG)}",
            re.DOTALL
        )
        
        if pattern.search(content):
            # Replace the existing section
            updated_content = pattern.sub(dashboard_html, content)
            logger.info("Found dashboard markers in existing README.md. Updating section...")
        else:
            # Markers not found, prepend dashboard or overwrite with beautiful default
            updated_content = get_default_readme(dashboard_html)
            logger.info("Dashboard markers not found in README.md. Initializing README with default layout...")
    else:
        # Create brand new file
        updated_content = get_default_readme(dashboard_html)
        logger.info("README.md does not exist. Creating new README.md...")

    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    logger.info("README.md successfully updated!")


if __name__ == "__main__":
    update_readme()
