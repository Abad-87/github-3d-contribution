"""Theme and color configurations for github-3d-contribution.

Supports Light and Dark themes across multiple color palettes
(GitHub Green, Ocean Blue, Neon Purple, and Sunset Orange).
"""

from typing import Dict, Any, List

# Define the standard color palettes
PALETTES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "green": {
        "dark": {
            "cube_faces": [
                {"top": "#21262d", "left": "#1a1e24", "right": "#1c2127"},  # L0
                {"top": "#0e4429", "left": "#0b3620", "right": "#0c3b24"},  # L1
                {"top": "#006d32", "left": "#005728", "right": "#00602c"},  # L2
                {"top": "#26a641", "left": "#1e8534", "right": "#219239"},  # L3
                {"top": "#39d353", "left": "#2da942", "right": "#32ba49"},  # L4
            ],
            "donut_colors": ["#39d353", "#26a641", "#006d32", "#0e4429", "#161b22"],
            "radar_fill": "rgba(57, 211, 83, 0.2)",
            "radar_stroke": "#39d353",
            "accent": "#39d353",
        },
        "light": {
            "cube_faces": [
                {"top": "#ebedf0", "left": "#bcbfc4", "right": "#d1d5db"},  # L0
                {"top": "#9be9a8", "left": "#7cb884", "right": "#8ad097"},  # L1
                {"top": "#40c463", "left": "#339c4e", "right": "#39ae58"},  # L2
                {"top": "#30a14e", "left": "#26813e", "right": "#2a8f45"},  # L3
                {"top": "#216e39", "left": "#1a582e", "right": "#1d6233"},  # L4
            ],
            "donut_colors": ["#216e39", "#30a14e", "#40c463", "#9be9a8", "#ebedf0"],
            "radar_fill": "rgba(48, 161, 78, 0.2)",
            "radar_stroke": "#30a14e",
            "accent": "#30a14e",
        }
    },
    "blue": {
        "dark": {
            "cube_faces": [
                {"top": "#161b22", "left": "#11151b", "right": "#13181f"},  # L0
                {"top": "#0d4b75", "left": "#0a3c5d", "right": "#0b4267"},  # L1
                {"top": "#1167b1", "left": "#0d528e", "right": "#0f5d9f"},  # L2
                {"top": "#187bcd", "left": "#1362a4", "right": "#156eb8"},  # L3
                {"top": "#2a9df4", "left": "#217dc3", "right": "#258ddc"},  # L4
            ],
            "donut_colors": ["#2a9df4", "#187bcd", "#1167b1", "#0d4b75", "#161b22"],
            "radar_fill": "rgba(42, 157, 244, 0.2)",
            "radar_stroke": "#2a9df4",
            "accent": "#2a9df4",
        },
        "light": {
            "cube_faces": [
                {"top": "#ebedf0", "left": "#bcbfc4", "right": "#d1d5db"},  # L0
                {"top": "#d0e1f9", "left": "#a6b4c7", "right": "#b8c8de"},  # L1
                {"top": "#4d8cd6", "left": "#3d70ab", "right": "#447ebe"},  # L2
                {"top": "#1e5fba", "left": "#184c95", "right": "#1a54a5"},  # L3
                {"top": "#093170", "left": "#072759", "right": "#082b63"},  # L4
            ],
            "donut_colors": ["#093170", "#1e5fba", "#4d8cd6", "#d0e1f9", "#ebedf0"],
            "radar_fill": "rgba(30, 95, 186, 0.2)",
            "radar_stroke": "#1e5fba",
            "accent": "#1e5fba",
        }
    },
    "purple": {
        "dark": {
            "cube_faces": [
                {"top": "#161b22", "left": "#11151b", "right": "#13181f"},  # L0
                {"top": "#3b1c6e", "left": "#2f1658", "right": "#341861"},  # L1
                {"top": "#5a2d9c", "left": "#48247d", "right": "#4f278a"},  # L2
                {"top": "#7e47d4", "left": "#6539aa", "right": "#6f3ebd"},  # L3
                {"top": "#ad72fc", "left": "#8a5bc9", "right": "#9864de"},  # L4
            ],
            "donut_colors": ["#ad72fc", "#7e47d4", "#5a2d9c", "#3b1c6e", "#161b22"],
            "radar_fill": "rgba(173, 114, 252, 0.2)",
            "radar_stroke": "#ad72fc",
            "accent": "#ad72fc",
        },
        "light": {
            "cube_faces": [
                {"top": "#ebedf0", "left": "#bcbfc4", "right": "#d1d5db"},  # L0
                {"top": "#e0c8ff", "left": "#b3a0cc", "right": "#c6b1e0"},  # L1
                {"top": "#ad72fc", "left": "#8a5bc9", "right": "#9864de"},  # L2
                {"top": "#7e47d4", "left": "#6539aa", "right": "#6f3ebd"},  # L3
                {"top": "#48199c", "left": "#39147d", "right": "#3f168a"},  # L4
            ],
            "donut_colors": ["#48199c", "#7e47d4", "#ad72fc", "#e0c8ff", "#ebedf0"],
            "radar_fill": "rgba(126, 71, 212, 0.2)",
            "radar_stroke": "#7e47d4",
            "accent": "#7e47d4",
        }
    },
    "orange": {
        "dark": {
            "cube_faces": [
                {"top": "#161b22", "left": "#11151b", "right": "#13181f"},  # L0
                {"top": "#5e2316", "left": "#4b1c11", "right": "#521e13"},  # L1
                {"top": "#a13b20", "left": "#812f19", "right": "#8d341c"},  # L2
                {"top": "#d9643a", "left": "#ae502e", "right": "#be5833"},  # L3
                {"top": "#fca36d", "left": "#ca8257", "right": "#dd8f5f"},  # L4
            ],
            "donut_colors": ["#fca36d", "#d9643a", "#a13b20", "#5e2316", "#161b22"],
            "radar_fill": "rgba(217, 100, 58, 0.2)",
            "radar_stroke": "#d9643a",
            "accent": "#d9643a",
        },
        "light": {
            "cube_faces": [
                {"top": "#ebedf0", "left": "#bcbfc4", "right": "#d1d5db"},  # L0
                {"top": "#fdd5c5", "left": "#caaab0", "right": "#ddbcad"},  # L1
                {"top": "#fca36d", "left": "#ca8257", "right": "#dd8f5f"},  # L2
                {"top": "#d9643a", "left": "#ae502e", "right": "#be5833"},  # L3
                {"top": "#a13b20", "left": "#812f19", "right": "#8d341c"},  # L4
            ],
            "donut_colors": ["#a13b20", "#d9643a", "#fca36d", "#fdd5c5", "#ebedf0"],
            "radar_fill": "rgba(217, 100, 58, 0.2)",
            "radar_stroke": "#d9643a",
            "accent": "#d9643a",
        }
    }
}

# General UI element theme values
THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "bg": "#090d16",
        "bg_glass": "rgba(13, 17, 23, 0.7)",
        "text": "#f0f6fc",
        "text_muted": "#8b949e",
        "border": "#21262d",
        "grid": "#30363d",
        "shadow": "rgba(0, 0, 0, 0.6)",
        "card_bg": "#0d1117"
    },
    "light": {
        "bg": "#ffffff",
        "bg_glass": "rgba(255, 255, 255, 0.8)",
        "text": "#1f2328",
        "text_muted": "#656d76",
        "border": "#d0d7de",
        "grid": "#e1e4e8",
        "shadow": "rgba(0, 0, 0, 0.1)",
        "card_bg": "#f6f8fa"
    }
}


def get_theme_colors(theme: str = "dark", palette: str = "green") -> Dict[str, Any]:
    """Retrieve color definitions for a specific theme and palette.

    Args:
        theme: Either 'dark' or 'light'.
        palette: Palette name ('green', 'blue', 'purple', 'orange').

    Returns:
        A dictionary containing color configs for cubes, radar, donut, and UI.
    """
    theme = theme.lower()
    palette = palette.lower()

    if theme not in ("dark", "light"):
        theme = "dark"
    if palette not in PALETTES:
        palette = "green"

    palette_colors = PALETTES[palette][theme]
    theme_ui = THEMES[theme]

    return {
        "theme": theme,
        "palette": palette,
        "bg": theme_ui["bg"],
        "bg_glass": theme_ui["bg_glass"],
        "text": theme_ui["text"],
        "text_muted": theme_ui["text_muted"],
        "border": theme_ui["border"],
        "grid": theme_ui["grid"],
        "shadow": theme_ui["shadow"],
        "card_bg": theme_ui["card_bg"],
        "cube_faces": palette_colors["cube_faces"],
        "donut_colors": palette_colors["donut_colors"],
        "radar_fill": palette_colors["radar_fill"],
        "radar_stroke": palette_colors["radar_stroke"],
        "accent": palette_colors["accent"],
    }
