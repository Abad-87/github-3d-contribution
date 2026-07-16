"""Radar Chart Generator for github-3d-contribution.

Processes stats, projects normalized values onto radial coordinates,
draws grid lines, axis dividers, labels, and the glowing data polygon.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import math
from typing import Dict, Any, List, Tuple

from src.utils import get_logger, save_svg_and_png
from src.colors import get_theme_colors
import src.svg as svg
import config

logger = get_logger("generate-radar")

# Define target ceiling values for logarithmic normalization
METRIC_CONFIGS = [
    {"key": "lifetime_commits", "label": "Commits", "target": 5000},
    {"key": "total_repositories", "label": "Repos", "target": 100},
    {"key": "total_stars", "label": "Stars", "target": 500},
    {"key": "total_forks", "label": "Forks", "target": 200},
    {"key": "lifetime_issues", "label": "Issues", "target": 200},
    {"key": "lifetime_prs", "label": "PRs", "target": 300},
    {"key": "lifetime_reviews", "label": "Reviews", "target": 200},
    {"key": "followers", "label": "Followers", "target": 500},
    {"key": "following", "label": "Following", "target": 200}
]


def normalize_value(val: float, target: float) -> float:
    """Normalizes a raw value log-scale to a score between 5 and 100.

    Ensures that empty charts are avoided and high-range values fit proportionally.
    """
    if val <= 0:
        return 8.0  # minimal center radius offset to keep polygon visible
        
    log_val = math.log1p(val)
    log_target = math.log1p(target)
    
    score = (log_val / log_target) * 100.0
    return max(8.0, min(100.0, score))


def format_label_val(val: int) -> str:
    """Formats raw integers into short readable strings (e.g., 1.5k)."""
    if val >= 1000:
        return f"{val / 1000.0:.1f}k"
    return str(val)


def generate_radar_chart() -> None:
    """Generates the stats radar chart SVG/PNG card."""
    stats_file = config.OUTPUT_DIR / "stats.json"
    
    if not stats_file.exists():
        logger.info(f"Required statistics file not found at {stats_file}. Cascading to stats compilation...")
        from src.stats import compile_stats
        stats = compile_stats()
    else:
        # Load stats
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

    # Get theme color palette
    theme_colors = get_theme_colors(config.THEME, os_palette_choice())
    
    # SVG Panel dimensions (Same as Donut for clean grid alignment in README)
    width = 440
    height = 260
    
    # Layout parameters
    cx, cy = 220.0, 138.0
    max_radius = 72.0
    
    svg_content = svg.create_svg_header(width, height, theme_colors, config.ANIMATED)
    
    # Draw card panel background
    svg_content += svg.draw_rect(
        x=2, y=2, w=width-4, h=height-4, rx=16, ry=16,
        fill=theme_colors["card_bg"],
        stroke=theme_colors["border"],
        stroke_width=1.5,
        filter_url="url(#card-shadow)" if config.SHADOWS else ""
    )
    
    # Draw card title
    svg_content += svg.draw_text(
        x=25, y=34,
        content="Developer Stats Profile",
        font_size=15,
        color=theme_colors["text"],
        weight="bold"
    )

    num_axes = len(METRIC_CONFIGS)
    
    # Precalculate angles for each axis
    angles = []
    for i in range(num_axes):
        # 0 index starts at top (-90 degrees)
        angle = i * (2 * math.pi / num_axes) - (math.pi / 2)
        angles.append(angle)

    # 1. Draw Concentric Grid Polygons (at 25%, 50%, 75%, 100% of max radius)
    grid_levels = [0.25, 0.5, 0.75, 1.0]
    for lvl in grid_levels:
        r_lvl = max_radius * lvl
        pts = []
        for angle in angles:
            px = cx + r_lvl * math.cos(angle)
            py = cy + r_lvl * math.sin(angle)
            pts.append(f"{px:.2f},{py:.2f}")
            
        pts_str = " ".join(pts)
        svg_content += f'    <polygon points="{pts_str}" fill="none" stroke="{theme_colors["grid"]}" stroke-width="0.8" opacity="0.45" />\n'

    # 2. Draw Axis Lines from center to boundary
    for i, angle in enumerate(angles):
        end_x = cx + max_radius * math.cos(angle)
        end_y = cy + max_radius * math.sin(angle)
        svg_content += svg.draw_line(
            x1=cx, y1=cy, x2=end_x, y2=end_y,
            color=theme_colors["grid"],
            width=1.0,
            opacity=0.4
        )

    # 3. Calculate data coordinates
    poly_points = []
    markers = []
    
    for i, cfg in enumerate(METRIC_CONFIGS):
        key = cfg["key"]
        target = cfg["target"]
        raw_val = stats.get(key, 0)
        
        # Logarithmic normalization
        score = normalize_value(float(raw_val), target)
        r_score = max_radius * (score / 100.0)
        
        angle = angles[i]
        px = cx + r_score * math.cos(angle)
        py = cy + r_score * math.sin(angle)
        
        poly_points.append(f"{px:.2f},{py:.2f}")
        
        # Save markers to draw on top of polygon later
        markers.append((px, py, theme_colors["accent"]))

    # 4. Draw Data Polygon
    poly_str = " ".join(poly_points)
    delay_style = ' style="animation: floatIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;"' if config.ANIMATED else ""
    class_attr = ' class="radar-area animate-item"' if config.ANIMATED else ' class="radar-area"'
    
    # Filled Area
    svg_content += f'    <polygon points="{poly_str}" fill="{theme_colors["radar_fill"]}" stroke="{theme_colors["radar_stroke"]}" stroke-width="2" filter="url(#accent-glow)"{class_attr}{delay_style} />\n'

    # 5. Draw Axis labels and values
    for i, cfg in enumerate(METRIC_CONFIGS):
        key = cfg["key"]
        label = cfg["label"]
        raw_val = stats.get(key, 0)
        formatted_val = format_label_val(raw_val)
        
        angle = angles[i]
        # Text is placed slightly beyond the maximum radius boundary
        label_dist = max_radius + 15.0
        lx = cx + label_dist * math.cos(angle)
        ly = cy + label_dist * math.sin(angle)
        
        # Adjust alignment dynamically depending on horizontal hemisphere position
        cos_val = math.cos(angle)
        if cos_val > 0.15:
            anchor = "start"
        elif cos_val < -0.15:
            anchor = "end"
        else:
            anchor = "middle"
            
        # Tweak vertical alignments slightly to prevent clipping
        sin_val = math.sin(angle)
        y_offset = 3.0
        if sin_val < -0.85:
            y_offset = -6.0
        elif sin_val > 0.85:
            y_offset = 12.0
            
        # Draw metric label
        svg_content += svg.draw_text(
            x=lx,
            y=ly + y_offset,
            content=f"{label}",
            font_size=10,
            color=theme_colors["text_muted"],
            anchor=anchor,
            weight="bold"
        )
        
        # Draw small value underneath the label
        svg_content += svg.draw_text(
            x=lx,
            y=ly + y_offset + 11.0,
            content=formatted_val,
            font_size=9,
            color=theme_colors["text"],
            anchor=anchor
        )

    # 6. Draw coordinate markers
    for mx, my, color in markers:
        svg_content += svg.draw_circle(
            cx=mx, cy=my, r=3.5,
            fill=color,
            stroke="#ffffff",
            stroke_width=1.0,
            extra_class="radar-marker"
        )

    svg_content += svg.create_svg_footer()
    
    svg_dest = config.OUTPUT_DIR / "radar.svg"
    png_dest = config.OUTPUT_DIR / "radar.png"
    
    save_svg_and_png(svg_content, svg_dest, png_dest)


def os_palette_choice() -> str:
    """Helper environment variable query for color schemes."""
    import os
    return os.getenv("PALETTE", "green")


if __name__ == "__main__":
    generate_radar_chart()
