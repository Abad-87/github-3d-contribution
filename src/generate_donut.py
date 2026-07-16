"""Language Donut Chart Generator for github-3d-contribution.

Loads user language stats, calculates slice angles with rounded edges,
places formatting indicators, and draws an interactive legend card.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from typing import Dict, Any, List

from src.utils import get_logger, save_svg_and_png
from src.colors import get_theme_colors
import src.svg as svg
import config

logger = get_logger("generate-donut")


def format_size(bytes_count: int) -> str:
    """Formats raw bytes into a human-readable string (KB, MB, etc.)."""
    if bytes_count <= 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    double_val = float(bytes_count)
    while double_val >= 1024.0 and i < len(units) - 1:
        double_val /= 1024.0
        i += 1
        
    return f"{double_val:.1f} {units[i]}"


def generate_donut_chart() -> None:
    """Generates the language donut chart SVG/PNG card."""
    stats_file = config.OUTPUT_DIR / "stats.json"
    
    if not stats_file.exists():
        logger.info(f"Required statistics file not found at {stats_file}. Cascading to stats compilation...")
        from src.stats import compile_stats
        stats = compile_stats()
    else:
        # Load compiled stats
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

    # Get style configurations
    theme_colors = get_theme_colors(config.THEME, os_palette_choice())
    
    # SVG Panel dimensions
    width = 440
    height = 260
    
    # Donut parameters
    cx, cy = 115.0, 135.0
    r_mid = 70.0
    thickness = 22.0
    
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
        content="Most Used Languages",
        font_size=15,
        color=theme_colors["text"],
        weight="bold"
    )

    languages: List[Dict[str, Any]] = stats.get("languages", [])
    total_bytes = stats.get("total_language_bytes", 0)
    
    # Drop-back circular grid representing the empty donut track
    svg_content += svg.draw_circle(
        cx=cx, cy=cy, r=r_mid,
        fill="none",
        stroke=theme_colors["grid"],
        stroke_width=thickness,
        opacity=0.3
    )

    if not languages or total_bytes == 0:
        # No languages found fallback
        svg_content += svg.draw_text(
            x=cx, y=cy,
            content="No Repo Data",
            font_size=12,
            color=theme_colors["text_muted"],
            anchor="middle"
        )
    else:
        # Calculate segments
        current_angle = 0.0
        # Limit to top 5 languages, group others if any
        top_languages = languages[:5]
        
        # Calculate if there are languages beyond top 5
        other_bytes = total_bytes - sum(lang["bytes"] for lang in top_languages)
        if other_bytes > 0 and len(languages) > 5:
            top_languages.append({
                "name": "Other",
                "bytes": other_bytes,
                "percentage": round((other_bytes / total_bytes) * 100, 1),
                "color": "#8b949e"
            })

        # Draw slices
        delay_unit = 0.1
        
        # Filter out slices that are too small to draw (less than 0.5%)
        visible_slices = [l for l in top_languages if l["percentage"] >= 0.5]
        
        # If there's only one language, draw a simple full circle
        if len(visible_slices) == 1:
            lang = visible_slices[0]
            svg_content += svg.draw_circle(
                cx=cx, cy=cy, r=r_mid,
                fill="none",
                stroke=lang["color"],
                stroke_width=thickness,
                extra_class="donut-slice animate-item"
            )
        else:
            for idx, lang in enumerate(visible_slices):
                pct = lang["percentage"]
                # segment span
                span = (pct / 100.0) * 360.0
                
                # Apply a slight gap margin between segments to look floating and premium
                gap = 3.0 if span > 8.0 else 0.0
                
                start_angle = current_angle + (gap / 2.0)
                end_angle = current_angle + span - (gap / 2.0)
                
                if (end_angle - start_angle) > 1.0:
                    path_str, _ = svg.get_donut_slice_path(cx, cy, r_mid, start_angle, end_angle)
                    
                    delay = idx * delay_unit
                    style_attr = f' style="animation-delay: {delay:.2f}s; transform-origin: {cx}px {cy}px;"' if config.ANIMATED else ""
                    class_attr = ' class="donut-slice animate-item"' if config.ANIMATED else ' class="donut-slice"'
                    
                    svg_content += f'        <path d="{path_str}" fill="none" stroke="{lang["color"]}" stroke-width="{thickness}" stroke-linecap="round"{class_attr}{style_attr} />\n'
                
                current_angle += span

        # Center text inside the donut hole
        svg_content += svg.draw_text(
            x=cx, y=cy - 6,
            content="TOTAL SIZE",
            font_size=9,
            color=theme_colors["text_muted"],
            anchor="middle",
            weight="bold",
            opacity=0.8
        )
        
        svg_content += svg.draw_text(
            x=cx, y=cy + 12,
            content=format_size(total_bytes),
            font_size=13,
            color=theme_colors["text"],
            anchor="middle",
            weight="bold"
        )

        # Draw the Legend Card on the right half
        legend_start_x = 220.0
        legend_start_y = 65.0
        row_height = 32.0
        
        for idx, lang in enumerate(top_languages):
            y_pos = legend_start_y + idx * row_height
            
            # Colored circle indicator
            svg_content += svg.draw_circle(
                cx=legend_start_x + 10,
                cy=y_pos - 4,
                r=6,
                fill=lang["color"]
            )
            
            # Language name label
            svg_content += svg.draw_text(
                x=legend_start_x + 26,
                y=y_pos,
                content=lang["name"],
                font_size=12,
                color=theme_colors["text"],
                weight="bold"
            )
            
            # Percentage (right-aligned)
            svg_content += svg.draw_text(
                x=width - 25,
                y=y_pos,
                content=f"{lang['percentage']}%",
                font_size=12,
                color=theme_colors["text_muted"],
                anchor="end"
            )
            
    svg_content += svg.create_svg_footer()
    
    svg_dest = config.OUTPUT_DIR / "language-donut.svg"
    png_dest = config.OUTPUT_DIR / "language-donut.png"
    
    save_svg_and_png(svg_content, svg_dest, png_dest)


def os_palette_choice() -> str:
    """Helper environment variable query for color schemes."""
    import os
    return os.getenv("PALETTE", "green")


if __name__ == "__main__":
    generate_donut_chart()
