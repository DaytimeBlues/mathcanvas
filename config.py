"""
MathCanvas Configuration
========================
Centralized configuration for colors, dimensions, and UI settings.
"""
from __future__ import annotations
from typing import Final

# ═══════════════════════════════════════════════════════════════════════════
# COLOR PALETTES
# ═══════════════════════════════════════════════════════════════════════════

# Premium drawing colors - carefully curated for visual appeal
COLORS: Final[dict[str, tuple[float, float, float, float]]] = {
    'charcoal': (0.15, 0.15, 0.18, 1.0),
    'crimson': (0.86, 0.20, 0.27, 1.0),
    'azure': (0.20, 0.60, 0.86, 1.0),
    'emerald': (0.18, 0.80, 0.44, 1.0),
    'amber': (0.96, 0.76, 0.07, 1.0),
    'orchid': (0.73, 0.33, 0.83, 1.0),
    'coral': (0.98, 0.50, 0.45, 1.0),
    'teal': (0.13, 0.69, 0.67, 1.0),
}

# Canvas background themes
CANVAS_BACKGROUNDS: Final[dict[str, tuple[float, float, float, float]]] = {
    'cream': (0.98, 0.96, 0.91, 1.0),  # Warm cream (like paper)
    'slate': (0.18, 0.20, 0.25, 1.0),  # Dark slate (chalkboard)
    'mint': (0.90, 0.98, 0.93, 1.0),   # Soft mint
}

DEFAULT_BACKGROUND: Final[str] = 'cream'

# UI element colors (hex for get_color_from_hex)
UI_COLORS: Final[dict[str, str]] = {
    'addition': '#4CAF50',
    'subtraction': '#FF6B6B',
    'multiplication': '#9B59B6',
    'done_button': '#2196F3',
    'gold': '#FFD700',
    'control_bar': (0.12, 0.14, 0.18, 0.9),
}

# ═══════════════════════════════════════════════════════════════════════════
# MATH OPERATIONS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

MATH_OPERATIONS: Final[dict[str, dict]] = {
    'add': {
        'symbol': '+',
        'header': '✨ ADDITION TIME ✨',
        'color': '#4CAF50',
        'emoji': '✨',
    },
    'subtract': {
        'symbol': '−',
        'header': '🌟 SUBTRACTION TIME 🌟',
        'color': '#FF6B6B',
        'emoji': '🌟',
    },
    'multiply': {
        'symbol': '×',
        'header': '🚀 MULTIPLICATION TIME 🚀',
        'color': '#9B59B6',
        'emoji': '🚀',
    },
}

# Unicorn reward emojis
UNICORNS: Final[list[str]] = ['🦄', '✨', '🌈', '⭐', '🎀', '💖', '🌟', '💫']

# ═══════════════════════════════════════════════════════════════════════════
# UI DIMENSIONS & LAYOUT
# ═══════════════════════════════════════════════════════════════════════════

# Control bar
CONTROL_BAR_HEIGHT_RATIO: Final[float] = 0.12
CONTROL_BAR_TOUCH_THRESHOLD: Final[float] = 0.88  # Touch above this Y% goes to controls

# Section width ratios (should sum to ~1.0)
PALETTE_SECTION_WIDTH: Final[float] = 0.35
TOOLS_SECTION_WIDTH: Final[float] = 0.25
MATH_SECTION_WIDTH: Final[float] = 0.30
SETTINGS_SECTION_WIDTH: Final[float] = 0.10

# Widget sizes
COLOR_BUTTON_SIZE: Final[tuple[int, int]] = (50, 50)
TOOL_BUTTON_WIDTH: Final[int] = 60
SMALL_BUTTON_WIDTH: Final[int] = 50

# Font sizes
FONT_EMOJI_LARGE: Final[int] = 28
FONT_EMOJI_MEDIUM: Final[int] = 24
FONT_MATH_OPERATOR: Final[int] = 36
FONT_PROBLEM_DISPLAY: Final[int] = 100
FONT_HINT: Final[int] = 24
FONT_HEADER: Final[int] = 32
FONT_UNICORN: Final[int] = 60

# Drawing defaults
DEFAULT_LINE_WIDTH: Final[int] = 4
MIN_LINE_WIDTH: Final[int] = 2
MAX_LINE_WIDTH: Final[int] = 15
ERASER_WIDTH_MULTIPLIER: Final[int] = 4

# Timing
UNICORN_CHECK_DELAY: Final[float] = 1.5  # seconds
UNICORN_IDLE_THRESHOLD: Final[float] = 1.0  # seconds
STROKE_RECENT_THRESHOLD: Final[float] = 3.0  # seconds

# Animation
UNICORN_FLOAT_DISTANCE: Final[int] = 150
UNICORN_ANIMATION_DURATION: Final[float] = 2.5
UNICORN_STAGGER_DELAY: Final[float] = 0.15
UNICORN_WIDGET_SIZE: Final[tuple[int, int]] = (80, 80)
MAX_ACTIVE_UNICORNS: Final[int] = 15

# Popup
POPUP_SIZE_HINT: Final[tuple[float, float]] = (0.85, 0.7)
POPUP_BUTTON_PADDING: Final[tuple[int, int]] = (50, 0)

# Control bar styling
CONTROL_BAR_RADIUS: Final[list[int]] = [0, 0, 20, 20]

# Undo/Redo
MAX_UNDO_STACK: Final[int] = 50

