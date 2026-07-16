"""Utility functions for github-3d-contribution.

Handles logging initialization, resilient HTTP request sessions, and
SVG to PNG conversion with graceful OS-level dependency fallbacks.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Default logger setup
def get_logger(name: str = "github-3d") -> logging.Logger:
    """Configures and retrieves a standard logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        # Console output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


logger = get_logger()


def get_http_session() -> requests.Session:
    """Create a requests session with robust retry logic for rate limits and server errors."""
    session = requests.Session()
    # Retry on typical transient errors or standard rate limit codes
    retries = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def save_svg_and_png(
    svg_content: str,
    svg_path: Path,
    png_path: Path
) -> bool:
    """Saves SVG content and attempts to convert it to PNG.

    Gracefully handles environments missing the system Cairo dependency.

    Args:
        svg_content: Raw SVG XML content.
        svg_path: Path destination to save the SVG file.
        png_path: Path destination to save the PNG file.

    Returns:
        True if both files saved successfully, False if PNG conversion failed
        but SVG was saved.
    """
    try:
        # Create output directories if they do not exist
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Write the SVG file
        with open(svg_path, "w", encoding="utf-8") as svg_file:
            svg_file.write(svg_content)
        logger.info(f"Successfully generated SVG: {svg_path}")

        # 2. Convert to PNG using cairosvg
        import cairosvg
        cairosvg.svg2png(
            bytestring=svg_content.encode("utf-8"),
            write_to=str(png_path)
        )
        logger.info(f"Successfully generated PNG: {png_path}")
        return True

    except (ImportError, OSError) as cairo_err:
        logger.warning(
            f"cairosvg or system Cairo libraries not available. "
            f"Skipped PNG generation for: {png_path.name}. "
            f"Details: {cairo_err}"
        )
        return False
    except Exception as exc:
        logger.error(
            f"Failed to generate output files for {svg_path.name}: {exc}",
            exc_info=True
        )
        return False
