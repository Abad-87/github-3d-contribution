"""Configuration module for github-3d-contribution.

Loads environment variables, manages user preferences, and establishes paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from local .env if it exists
load_dotenv()

# ---------------------------------------------------------
# GitHub Authentication & User Configuration
# ---------------------------------------------------------
# Personal Access Token (PAT) with read:user and repo scopes
GITHUB_TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

# GitHub Username for stats collection
USERNAME = os.getenv("GITHUB_USERNAME", "Abad-87")

# ---------------------------------------------------------
# Directory Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Theme & Layout Configuration
# ---------------------------------------------------------
# Base theme choice: 'dark' or 'light'
THEME = os.getenv("THEME", "dark").lower()
if THEME not in ("dark", "light"):
    THEME = "dark"

# System font stack to ensure neat rendering across devices
FONT_FAMILY = os.getenv(
    "FONT_FAMILY",
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
)

# Visual properties
ANIMATED = os.getenv("ANIMATED", "true").lower() in ("true", "1", "yes")
SHADOWS = os.getenv("SHADOWS", "true").lower() in ("true", "1", "yes")

# Validate configuration
if not GITHUB_TOKEN:
    import warnings
    warnings.warn(
        "No GITHUB_TOKEN or GH_TOKEN found in environment. "
        "API rate limits will be severely restricted and some calls may fail."
    )
