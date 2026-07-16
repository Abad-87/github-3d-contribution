"""SVG generation utility library for github-3d-contribution.

Provides coordinates math, standard template wrappers, CSS injectors,
glow and shadow filters, and vector drawing helpers for SVG generation.
"""

import math
from typing import Dict, Any, List, Tuple


def get_svg_filters() -> str:
    """Returns SVG filter definitions for drop shadows and glowing effects."""
    return """
    <defs>
        <!-- Soft drop shadow for isometric elements -->
        <filter id="cube-shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#000000" flood-opacity="0.35"/>
        </filter>
        
        <!-- Drop shadow for text and cards -->
        <filter id="card-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
        </filter>

        <!-- Glow filter for radar outlines and accents -->
        <filter id="accent-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feComponentTransfer in="blur" result="glow">
                <feFuncA type="linear" slope="0.5"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode in="glow"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    """


def get_base_css(theme: Dict[str, Any], animated: bool = True) -> str:
    """Generates CSS stylesheet for the SVG, containing interactive classes and animations."""
    animation_css = ""
    if animated:
        animation_css = """
        @keyframes floatIn {
            0% {
                transform: translateY(30px);
                opacity: 0;
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }
        .animate-item {
            animation: floatIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        """

    return f"""
    <style>
        .svg-container {{
            font-family: {config_font_family()};
            background-color: transparent;
        }}
        
        /* Grid and borders */
        .grid-line {{
            stroke: {theme["grid"]};
            stroke-width: 1;
            opacity: 0.5;
        }}
        .border-line {{
            stroke: {theme["border"]};
            stroke-width: 1.5;
        }}
        
        /* Interactive 3D cubes */
        .cube-group {{
            transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), filter 0.25s ease;
            cursor: pointer;
        }}
        .cube-group:hover {{
            transform: translateY(-8px);
            filter: brightness(1.2) drop-shadow(0 12px 16px {theme["shadow"]});
        }}
        
        /* Donut slice hover logic */
        .donut-slice {{
            transition: stroke-width 0.2s ease, filter 0.2s ease, opacity 0.2s ease;
            cursor: pointer;
        }}
        .donut-slice:hover {{
            stroke-width: 34 !important;
            filter: brightness(1.15) drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
            opacity: 1 !important;
        }}

        /* Radar chart hover items */
        .radar-area {{
            transition: fill-opacity 0.3s ease, stroke-width 0.3s ease;
        }}
        .radar-area:hover {{
            fill-opacity: 0.35;
            stroke-width: 3px;
        }}
        .radar-marker {{
            transition: r 0.2s ease, fill 0.2s ease;
        }}
        .radar-marker:hover {{
            r: 7;
            fill: #ffffff;
        }}
        
        {animation_css}
    </style>
    """


def config_font_family() -> str:
    """Helper import wrapper to fetch font settings."""
    import config
    return config.FONT_FAMILY


def create_svg_header(
    width: int,
    height: int,
    theme: Dict[str, Any],
    animated: bool = True
) -> str:
    """Builds the SVG header including viewport, styling block, and filter defs."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" class="svg-container">
    {get_base_css(theme, animated)}
    {get_svg_filters()}
    """


def create_svg_footer() -> str:
    """Closes the SVG tag."""
    return "\n</svg>"


def draw_isometric_cube(
    cx: float,
    cy: float,
    col: int,
    row: int,
    h: float,
    level: int,
    theme: Dict[str, Any],
    animated: bool = True,
    delay: float = 0.0
) -> str:
    """Generates the SVG path structures representing one 3D isometric cube.

    Coordinates calculation details:
    Top, Left, and Right faces are projected to make it look like a solid column.
    
    Args:
        cx: Projected X coordinate for the top-corner of the cell base.
        cy: Projected Y coordinate for the top-corner of the cell base.
        col: Week grid coordinate (0 to 52).
        row: Day grid coordinate (0 to 6).
        h: Cube height.
        level: Contribution level index (0 to 4).
        theme: Dict containing the styling colors.
        animated: True to enable delay injection.
        delay: Fade-in start offset (seconds).
    """
    faces = theme["cube_faces"][level]
    
    # 3D offsets for projection points
    # Base rhombus corners (z = 0)
    # p_top = (cx, cy)
    # p_left = (cx - 14, cy + 7)
    # p_right = (cx + 14, cy + 7)
    # p_bottom = (cx, cy + 14)
    
    # Lifted top rhombus corners (z = h)
    t_top_x, t_top_y = cx, cy - h
    t_left_x, t_left_y = cx - 14, cy + 7 - h
    t_right_x, t_right_y = cx + 14, cy + 7 - h
    t_bottom_x, t_bottom_y = cx, cy + 14 - h

    # CSS Delay template
    delay_style = f' style="animation-delay: {delay:.3f}s;"' if animated else ""
    class_attr = ' class="cube-group animate-item"' if animated else ' class="cube-group"'
    
    # Wrap in a group for unified hover transitions and floating animations
    svg_cube = f'    <g{class_attr}{delay_style} data-col="{col}" data-row="{row}">\n'
    
    # 1. Left Face (Only visible for values > 0 or base heights)
    # SVG Path: TopLeft -> BottomLeft -> Bottom -> TopRight
    svg_cube += f'        <path d="M {t_left_x},{t_left_y} L {t_bottom_x},{t_bottom_y} L {cx},{cy + 14} L {cx - 14},{cy + 7} Z" fill="{faces["left"]}" />\n'
    
    # 2. Right Face
    # SVG Path: BottomLeft -> TopRight -> BottomRight -> Bottom
    svg_cube += f'        <path d="M {t_bottom_x},{t_bottom_y} L {t_right_x},{t_right_y} L {cx + 14},{cy + 7} L {cx},{cy + 14} Z" fill="{faces["right"]}" />\n'
    
    # 3. Top Face (Rhombus)
    # SVG Path: Top -> Left -> Bottom -> Right
    svg_cube += f'        <path d="M {t_top_x},{t_top_y} L {t_left_x},{t_left_y} L {t_bottom_x},{t_bottom_y} L {t_right_x},{t_right_y} Z" fill="{faces["top"]}" />\n'
    
    # If the user hovers, show standard tooltip support
    svg_cube += '    </g>\n'
    return svg_cube


def get_donut_slice_path(
    cx: float,
    cy: float,
    r: float,
    start_angle: float,
    end_angle: float
) -> Tuple[str, int]:
    """Generates the SVG path representation of a circular arc for donut charts.

    Angles are calculated in radians.

    Returns:
        A tuple of (path string, large arc flag).
    """
    # Convert degrees to radians (offsetting to start from top)
    rad_start = math.radians(start_angle - 90)
    rad_end = math.radians(end_angle - 90)
    
    # Calculate point positions
    x_start = cx + r * math.cos(rad_start)
    y_start = cy + r * math.sin(rad_start)
    x_end = cx + r * math.cos(rad_end)
    y_end = cy + r * math.sin(rad_end)
    
    # Determine the large arc flag
    large_arc = 1 if (end_angle - start_angle) > 180 else 0
    
    path = f"M {x_start:.2f} {y_start:.2f} A {r:.2f} {r:.2f} 0 {large_arc} 1 {x_end:.2f} {y_end:.2f}"
    return path, large_arc


def draw_text(
    x: float,
    y: float,
    content: str,
    font_size: int,
    color: str,
    anchor: str = "start",
    weight: str = "normal",
    opacity: float = 1.0,
    extra_class: str = ""
) -> str:
    """Generates standard SVG text element."""
    class_str = f' class="{extra_class}"' if extra_class else ""
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{font_size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" opacity="{opacity:.2f}"{class_str}>{content}</text>'


def draw_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str,
    width: float = 1.0,
    opacity: float = 1.0,
    dasharray: str = ""
) -> str:
    """Generates standard SVG line element."""
    dash_attr = f' stroke-dasharray="{dasharray}"' if dasharray else ""
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width:.2f}" opacity="{opacity:.2f}"{dash_attr} />'


def draw_circle(
    cx: float,
    cy: float,
    r: float,
    fill: str,
    stroke: str = "none",
    stroke_width: float = 0.0,
    opacity: float = 1.0,
    extra_class: str = "",
    filter_url: str = ""
) -> str:
    """Generates standard SVG circle element."""
    stroke_attr = f' stroke="{stroke}" stroke-width="{stroke_width:.2f}"' if stroke_width > 0 else ""
    class_attr = f' class="{extra_class}"' if extra_class else ""
    filter_attr = f' filter="{filter_url}"' if filter_url else ""
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" opacity="{opacity:.2f}"{stroke_attr}{class_attr}{filter_attr} />'


def draw_rect(
    x: float,
    y: float,
    w: float,
    h: float,
    rx: float,
    ry: float,
    fill: str,
    stroke: str = "none",
    stroke_width: float = 0.0,
    opacity: float = 1.0,
    filter_url: str = ""
) -> str:
    """Generates standard SVG rect element (with rounded corners)."""
    stroke_attr = f' stroke="{stroke}" stroke-width="{stroke_width:.2f}"' if stroke_width > 0 else ""
    filter_attr = f' filter="{filter_url}"' if filter_url else ""
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{fill}" opacity="{opacity:.2f}"{stroke_attr}{filter_attr} />'
