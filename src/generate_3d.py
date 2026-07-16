"""3D Isometric Contribution Calendar Generator for github-3d-contribution.

Applies isometric projection coordinates to render the 53 weeks x 7 days grid
as realistic columns with 3D faces, shadows, legends, and month headers.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import datetime
from typing import Dict, Any, List

from src.utils import get_logger, save_svg_and_png
from src.colors import get_theme_colors
import src.svg as svg
import config

logger = get_logger("generate-3d")


def get_month_labels(contributions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculates month transition labels with projected isometric coordinates."""
    labels = []
    seen_months = set()
    
    # Sort days chronologically
    sorted_days = sorted(contributions, key=lambda d: d["date"])
    
    col = 0
    for idx, day in enumerate(sorted_days):
        date_obj = datetime.datetime.strptime(day["date"], "%Y-%m-%d").date()
        row = (date_obj.weekday() + 1) % 7
        if row == 0 and idx > 0:
            col += 1
            
        month_key = date_obj.strftime("%b")
        if month_key not in seen_months:
            if row == 0 or idx < 7:
                labels.append({
                    "text": month_key,
                    "col": col,
                    "row": 0
                })
                seen_months.add(month_key)
                
    return labels


def draw_legend(
    start_x: float,
    start_y: float,
    theme: Dict[str, Any],
    animated: bool = True
) -> str:
    """Renders a beautiful 3D contribution level legend at the bottom right."""
    svg_legend = ""
    
    # "Less" Label
    svg_legend += svg.draw_text(
        start_x - 10,
        start_y + 12,
        "Less",
        11,
        theme["text_muted"],
        anchor="end"
    )
    
    # Draw 5 tiny isometric cubes side-by-side representing levels 0 to 4
    for lvl in range(5):
        # We compute local coordinates for the tiny cubes
        cube_cx = start_x + lvl * 26
        cube_cy = start_y
        
        # Draw a small 3D cube
        svg_legend += svg.draw_isometric_cube(
            cx=cube_cx,
            cy=cube_cy,
            col=99,  # dummy col/row to avoid interference
            row=99,
            h=6 + lvl * 3,  # height scales with level
            level=lvl,
            theme=theme,
            animated=animated,
            delay=0.1
        )
        
    # "More" Label
    svg_legend += svg.draw_text(
        start_x + 5 * 26,
        start_y + 12,
        "More",
        11,
        theme["text_muted"],
        anchor="start"
    )
    
    return svg_legend


def generate_3d_graph() -> None:
    """Main rendering execution.

    Loads contributions from data/contributions.json, projects coordinates,
    applies themes, and renders the 3D graph.
    """
    contrib_file = config.DATA_DIR / "contributions.json"
    if not contrib_file.exists():
        logger.info("contributions.json is missing. Cascading to fetch contributions...")
        from src.fetch_contributions import fetch_all
        fetch_all(config.USERNAME, config.GITHUB_TOKEN)

    with open(contrib_file, "r", encoding="utf-8") as f:
        contributions = json.load(f)

    # Sort chronologically to make sure calculations are correct
    contributions.sort(key=lambda d: d["date"])

    # Calculate statistics from the contributions array directly
    total_contribs = sum(day["count"] for day in contributions)
    
    # Streaks calculation
    longest_streak = 0
    temp_streak = 0
    for day in contributions:
        if day["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    calendar_last_date_str = contributions[-1]["date"]
    calendar_last_date = datetime.datetime.strptime(calendar_last_date_str, "%Y-%m-%d").date()

    last_contrib_idx = -1
    for i in range(len(contributions) - 1, -1, -1):
        if contributions[i]["count"] > 0:
            last_contrib_idx = i
            break

    current_streak = 0
    if last_contrib_idx != -1:
        last_contrib_date = datetime.datetime.strptime(contributions[last_contrib_idx]["date"], "%Y-%m-%d").date()
        if (calendar_last_date - last_contrib_date).days <= 1:
            for i in range(last_contrib_idx, -1, -1):
                if contributions[i]["count"] > 0:
                    current_streak += 1
                else:
                    break

    # Get style rules
    theme_colors = get_theme_colors(config.THEME, os_palette_choice())
    
    # Establish Canvas dimensions
    width = 840
    height = 450
    
    # Isometric steps
    center_x = 138.0
    center_y = 65.0
    
    # 1. Start SVG Header
    svg_content = svg.create_svg_header(width, height, theme_colors, config.ANIMATED)
    
    # 2. Draw card background panel
    svg_content += svg.draw_rect(
        x=2, y=2, w=width-4, h=height-4, rx=16, ry=16,
        fill=theme_colors["card_bg"],
        stroke=theme_colors["border"],
        stroke_width=1.5,
        filter_url="url(#card-shadow)" if config.SHADOWS else ""
    )
    
    # 3. Draw headers
    display_name = config.USERNAME
    
    svg_content += svg.draw_text(
        x=30, y=38,
        content=f"{display_name}'s 3D Contributions",
        font_size=18,
        color=theme_colors["text"],
        weight="bold"
    )
    
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    svg_content += svg.draw_text(
        x=30, y=56,
        content=f"{total_contribs} contributions in the last year • Updated: {date_str}",
        font_size=12,
        color=theme_colors["text_muted"]
    )
    
    # 4. Generate month labels
    month_labels = get_month_labels(contributions)
    for lbl in month_labels:
        col_x = center_x + lbl["col"] * 12.0 - lbl["row"] * 12.0
        col_y = center_y + lbl["col"] * 6.0 + lbl["row"] * 6.0
        
        svg_content += svg.draw_text(
            x=col_x,
            y=col_y - 12.0,
            content=lbl["text"],
            font_size=10,
            color=theme_colors["text_muted"],
            anchor="middle",
            opacity=0.85
        )

    # 5. Draw weekday labels along the left boundary (row 1, 3, 5)
    days_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row_idx, day_name in days_labels.items():
        lbl_x = center_x - 1 * 12.0 - row_idx * 12.0
        lbl_y = center_y - 1 * 6.0 + row_idx * 6.0 + 10.0
        svg_content += svg.draw_text(
            x=lbl_x,
            y=lbl_y,
            content=day_name,
            font_size=10,
            color=theme_colors["text_muted"],
            anchor="end",
            opacity=0.85
        )
        
    # 6. Render the 3D contribution grid (Painter's algorithm: Back-to-Front)
    delay_unit = 0.003
    
    level_indices = {
        "NONE": 0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE": 2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE": 4
    }

    # Group flat list of contributions into a coordinate grid
    grid = {}
    col_idx = 0
    for idx, day in enumerate(contributions):
        date_obj = datetime.datetime.strptime(day["date"], "%Y-%m-%d").date()
        day_idx = (date_obj.weekday() + 1) % 7
        if day_idx == 0 and idx > 0:
            col_idx += 1
        grid[(col_idx, day_idx)] = day
            
    # Iterate and render
    max_cols = max((k[0] for k in grid.keys())) + 1 if grid else 53
    
    for c in range(max_cols):
        for r in range(7):
            cell = grid.get((c, r))
            if not cell:
                continue
                
            level_str = cell.get("level", "NONE")
            level_idx = level_indices.get(level_str, 0)
            
            # Cube height mapping: h = count * 3 (or 2.0 baseline for 0)
            count = cell.get("count", 0)
            h = float(count) * 3.0 if count > 0 else 2.0
            
            cx = center_x + c * 12.0 - r * 12.0
            cy = center_y + c * 6.0 + r * 6.0
            
            delay = (c + r) * delay_unit
            
            svg_content += svg.draw_isometric_cube(
                cx=cx,
                cy=cy,
                col=c,
                row=r,
                h=h,
                level=level_idx,
                theme=theme_colors,
                animated=config.ANIMATED,
                delay=delay
            )
            
    # 7. Render streaks card and info at the bottom-left
    card_y = 385
    svg_content += svg.draw_text(
        x=30, y=card_y + 12,
        content=f"Current Streak: {current_streak} days",
        font_size=12,
        color=theme_colors["text"],
        weight="bold"
    )
    svg_content += svg.draw_text(
        x=30, y=card_y + 28,
        content=f"Longest Streak: {longest_streak} days",
        font_size=12,
        color=theme_colors["text_muted"]
    )
    
    # 8. Render the 3D legend at the bottom-right
    svg_content += draw_legend(
        start_x=590.0,
        start_y=395.0,
        theme=theme_colors,
        animated=config.ANIMATED
    )
    
    # 9. Close and save
    svg_content += svg.create_svg_footer()
    
    svg_dest = config.OUTPUT_DIR / "contribution-3d.svg"
    png_dest = config.OUTPUT_DIR / "contribution-3d.png"
    
    save_svg_and_png(svg_content, svg_dest, png_dest)


def os_palette_choice() -> str:
    """Helper environment variable query for color schemes."""
    import os
    return os.getenv("PALETTE", "green")


if __name__ == "__main__":
    generate_3d_graph()
    print("REAL CONTRIBUTION SYNC ENABLED")
