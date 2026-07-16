"""3D Isometric Contribution Calendar Generator for github-3d-contribution.

Applies isometric projection coordinates to render the 53 weeks x 7 days grid
as realistic columns with 3D faces, shadows, legends, and month headers.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List

from src.utils import get_logger, save_svg_and_png
from src.colors import get_theme_colors
import src.svg as svg
import config

logger = get_logger("generate-3d")


def get_month_labels(days: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculates month transition labels with projected isometric coordinates.

    Identifies the transition points where a new month starts in the calendar,
    so that labels can be placed above the appropriate weeks.
    """
    labels = []
    seen_months = set()
    
    # Sort days chronologically
    sorted_days = sorted(days, key=lambda d: d["date"])
    
    for idx, day in enumerate(sorted_days):
        date_obj = datetime.datetime.strptime(day["date"], "%Y-%m-%d").date()
        month_key = date_obj.strftime("%b")  # e.g., "Jan"
        
        # Calculate grid coordinates
        col = idx // 7
        row = idx % 7
        
        # If it's a new month and we're on Sunday (row 0), place a label
        # Or if it's the very start of the calendar, place the month label
        if month_key not in seen_months:
            # We want to label at row 0 (Sunday) to align nicely
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

    Loads processed statistics, projects grid coordinates, applies themes,
    and writes files.
    """
    raw_file = config.DATA_DIR / "raw_data.json"
    stats_file = config.OUTPUT_DIR / "stats.json"
    
    if not stats_file.exists() or not raw_file.exists():
        logger.info("Required data or stats files are missing. Cascading to stats compilation...")
        from src.stats import compile_stats
        stats = compile_stats()
        # Reload raw data as it was created/updated during compile_stats cascade
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    else:
        # Load existing data
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

    # Get style rules
    theme_colors = get_theme_colors(config.THEME, os_palette_choice())
    
    # Establish Canvas dimensions
    width = 840
    height = 450
    
    # Isometric steps
    # Week step: (12, 6) -> 12px right, 6px down
    # Day step: (-12, 6) -> 12px left, 6px down
    # center_x is placed so that the minimum X coordinate (col=0, row=6 -> -72) stays inside margins
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
    display_name = stats.get("display_name", stats["username"])
    total_contribs = stats.get("total_contributions", 0)
    
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
    calendar_days = []
    weeks = raw_data["graphql"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    for week in weeks:
        for day in week["contributionDays"]:
            calendar_days.append(day)
            
    month_labels = get_month_labels(calendar_days)
    for lbl in month_labels:
        # Project month label position along the row=0 edge
        col_x = center_x + lbl["col"] * 12.0 - lbl["row"] * 12.0
        col_y = center_y + lbl["col"] * 6.0 + lbl["row"] * 6.0
        
        svg_content += svg.draw_text(
            x=col_x,
            y=col_y - 12.0,  # floating slightly above the grid
            content=lbl["text"],
            font_size=10,
            color=theme_colors["text_muted"],
            anchor="middle",
            opacity=0.85
        )

    # 5. Draw weekday labels along the left boundary (row 1, 3, 5)
    days_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row_idx, day_name in days_labels.items():
        # Project left of col = 0
        lbl_x = center_x - 1 * 12.0 - row_idx * 12.0
        lbl_y = center_y - 1 * 6.0 + row_idx * 6.0 + 10.0 # slight y adjustment
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
    # Sort or double loop ensuring columns and rows are processed sequentially
    delay_unit = 0.003  # ripple rate delay per cell
    
    # Level to height mapping
    level_heights = {
        "NONE": 3.0,
        "FIRST_QUARTILE": 12.0,
        "SECOND_QUARTILE": 22.0,
        "THIRD_QUARTILE": 34.0,
        "FOURTH_QUARTILE": 46.0
    }
    
    level_indices = {
        "NONE": 0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE": 2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE": 4
    }

    # Flatten weeks structure to a grid
    grid = {}
    for col_idx, week in enumerate(weeks):
        for day_idx, day in enumerate(week["contributionDays"]):
            # weekday matches day_idx
            grid[(col_idx, day_idx)] = day
            
    # Iterate and render
    for col_idx in range(53):
        for day_idx in range(7):
            cell = grid.get((col_idx, day_idx))
            if not cell:
                continue
                
            level_str = cell.get("contributionLevel", "NONE")
            level_idx = level_indices.get(level_str, 0)
            h = level_heights.get(level_str, 3.0)
            
            # Project base point
            cx = center_x + col_idx * 12.0 - day_idx * 12.0
            cy = center_y + col_idx * 6.0 + day_idx * 6.0
            
            delay = (col_idx + day_idx) * delay_unit
            
            svg_content += svg.draw_isometric_cube(
                cx=cx,
                cy=cy,
                col=col_idx,
                row=day_idx,
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
        content=f"Current Streak: {stats.get('current_streak', 0)} days",
        font_size=12,
        color=theme_colors["text"],
        weight="bold"
    )
    svg_content += svg.draw_text(
        x=30, y=card_y + 28,
        content=f"Longest Streak: {stats.get('longest_streak', 0)} days",
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
