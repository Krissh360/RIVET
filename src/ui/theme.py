"""
src/ui/theme.py
---------------
Design tokens for RIVET UI (Light Theme).
All color, typography, spacing, radius, and tier tokens are centralized here.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
PRIMARY = "#335b49"
PRIMARY_FOREGROUND = "#ffffff"
PRIMARY_HOVER = "#274839"

SECONDARY = "#eaeaeb"
SECONDARY_FOREGROUND = "#303036"

ACCENT = "#e5ebe8"
ACCENT_FOREGROUND = "#2e5242"

BACKGROUND = "#f7f7f8"
FOREGROUND = "#1d1d20"

CARD = "#ffffff"
CARD_FOREGROUND = "#1d1d20"
CARD_SHADOW = "0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)"

MUTED = "#efeff0"
MUTED_FOREGROUND = "#68686e"

# Converted from HSL
BORDER = "#d5d5d8"        # HSL(240 4% 84%)
INPUT_BORDER = "#cfcfd3"  # HSL(240 4% 82%)
RING = "#335b49"          # HSL(153 28% 28%)

# Chart Palette (converted from HSL)
CHART_1 = "#40725c"       # HSL(153 28% 35%) - Green
CHART_2 = "#4375b1"       # HSL(213 45% 48%) - Blue
CHART_3 = "#ad722e"       # HSL(32 58% 43%)  - Amber
CHART_4 = "#7f5ca3"       # HSL(270 28% 50%) - Purple
CHART_5 = "#af4b5c"       # HSL(350 40% 49%) - Rose

CHART_PALETTE = [CHART_1, CHART_2, CHART_3, CHART_4, CHART_5]

# Tier colors mapped to chart tokens
LABEL_ORDER = ["Poor", "Average", "Good", "Excellent"]

TIER_COLORS = {
    "Poor": CHART_5,       # Rose (#af4b5c)
    "Average": CHART_3,    # Amber (#ad722e)
    "Good": CHART_2,       # Blue (#4375b1)
    "Excellent": CHART_1,  # Green (#40725c)
}

# Soft alert / review card tokens
WARNING_BG = "#fdf8f0"
WARNING_BORDER = CHART_3
WARNING_FOREGROUND = "#8c561b"

# ---------------------------------------------------------------------------
# Shape and Spacing (Base unit = 0.23rem)
# ---------------------------------------------------------------------------
SPACING_BASE_UNIT = "0.23rem"
SPACING_1 = "0.23rem"
SPACING_2 = "0.46rem"
SPACING_3 = "0.69rem"
SPACING_4 = "0.92rem"
SPACING_6 = "1.38rem"
SPACING_8 = "1.84rem"
SPACING_10 = "2.30rem"
SPACING_12 = "2.76rem"

RADIUS_BASE = "2rem"      # Cards, primary buttons, tabs, containers
RADIUS_INPUT = "1rem"     # Inputs, selectboxes, textareas
RADIUS_BADGE = "9999px"   # Pill badges
RADIUS_ALERT = "1rem"     # Callouts and alert cards

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_SANS = "'Raleway', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_SERIF = "Georgia, Cambria, 'Times New Roman', Times, serif"
FONT_MONO = "'Roboto Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
