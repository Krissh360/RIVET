"""
src/ui/styles.py
----------------
CSS injection and layout styling for RIVET design system.
"""

from __future__ import annotations
import streamlit as st
from src.ui.theme import (
    PRIMARY,
    PRIMARY_FOREGROUND,
    PRIMARY_HOVER,
    SECONDARY,
    SECONDARY_FOREGROUND,
    ACCENT,
    ACCENT_FOREGROUND,
    BACKGROUND,
    FOREGROUND,
    CARD,
    CARD_SHADOW,
    MUTED,
    MUTED_FOREGROUND,
    BORDER,
    INPUT_BORDER,
    RING,
    CHART_1,
    CHART_2,
    CHART_3,
    CHART_4,
    CHART_5,
    WARNING_BG,
    WARNING_BORDER,
    WARNING_FOREGROUND,
    RADIUS_BASE,
    RADIUS_INPUT,
    RADIUS_BADGE,
    RADIUS_ALERT,
    FONT_SANS,
    FONT_MONO,
    SPACING_1,
    SPACING_2,
    SPACING_3,
    SPACING_4,
    SPACING_6,
    SPACING_8,
)


def get_css() -> str:
    """Return the complete CSS string matching the RIVET design system."""
    return f"""
    <style>
    /* -----------------------------------------------------------------------
       Typography & Font Loading
       ----------------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700;800&family=Roboto+Mono:wght@400;500;600;700&display=swap');

    @font-face {{
        font-family: 'Raleway';
        src: url('/app/static/fonts/raleway-400.woff2') format('woff2');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }}
    @font-face {{
        font-family: 'Raleway';
        src: url('/app/static/fonts/raleway-600.woff2') format('woff2');
        font-weight: 600;
        font-style: normal;
        font-display: swap;
    }}
    @font-face {{
        font-family: 'Raleway';
        src: url('/app/static/fonts/raleway-700.woff2') format('woff2');
        font-weight: 700;
        font-style: normal;
        font-display: swap;
    }}
    @font-face {{
        font-family: 'Roboto Mono';
        src: url('/app/static/fonts/roboto-mono-400.woff2') format('woff2');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }}
    @font-face {{
        font-family: 'Roboto Mono';
        src: url('/app/static/fonts/roboto-mono-600.woff2') format('woff2');
        font-weight: 600;
        font-style: normal;
        font-display: swap;
    }}

    /* Global body & container styles */
    html, body, [class*="css"], .stApp {{
        font-family: {FONT_SANS};
        color: {FOREGROUND};
        background-color: {BACKGROUND};
    }}

    /* Hide Streamlit default header, footer, and menu */
    #MainMenu {{ visibility: hidden; display: none; }}
    footer {{ visibility: hidden; display: none; }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Main container padding */
    .block-container {{
        padding-top: {SPACING_4};
        padding-bottom: {SPACING_8};
        max-width: 1140px;
    }}

    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {FONT_SANS};
        font-weight: 700;
        color: {FOREGROUND};
        letter-spacing: -0.01em;
    }}

    /* Mono text: numbers, metrics, code, probabilities */
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"],
    code, pre, .mono {{
        font-family: {FONT_MONO} !important;
    }}

    [data-testid="stMetricLabel"] {{
        font-family: {FONT_SANS} !important;
        color: {MUTED_FOREGROUND} !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* -----------------------------------------------------------------------
       Header & Hero Components
       ----------------------------------------------------------------------- */
    .rivet-top-header {{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: {SPACING_3};
        padding: {SPACING_3} 0;
        border-bottom: 1px solid {BORDER};
        margin-bottom: {SPACING_6};
    }}

    .rivet-logo-mark {{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: {PRIMARY};
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: {PRIMARY_FOREGROUND};
        font-family: {FONT_SANS};
        font-weight: 800;
        font-size: 0.95rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }}

    .rivet-wordmark {{
        font-family: {FONT_SANS};
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: {FOREGROUND};
    }}

    .rivet-hero {{
        text-align: center;
        margin: {SPACING_4} auto {SPACING_8} auto;
        max-width: 820px;
    }}

    .rivet-hero-title {{
        font-family: {FONT_SANS};
        font-size: 3.4rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: {FOREGROUND};
        line-height: 1.05;
        margin-bottom: {SPACING_2};
    }}

    .rivet-hero-subtitle {{
        font-family: {FONT_SANS};
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        color: {MUTED_FOREGROUND};
        text-transform: uppercase;
        margin-bottom: {SPACING_4};
    }}

    .rivet-hero-headline {{
        font-family: {FONT_SANS};
        font-size: 1.85rem;
        font-weight: 700;
        color: {FOREGROUND};
        margin-bottom: {SPACING_3};
        line-height: 1.3;
    }}

    .rivet-hero-headline-highlight {{
        color: {PRIMARY};
        font-style: italic;
    }}

    .rivet-hero-desc {{
        font-family: {FONT_SANS};
        font-size: 1.02rem;
        color: {MUTED_FOREGROUND};
        line-height: 1.6;
        max-width: 660px;
        margin: 0 auto;
    }}

    /* -----------------------------------------------------------------------
       Stat Cards Row
       ----------------------------------------------------------------------- */
    .rivet-stat-card {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_BASE};
        padding: {SPACING_6} {SPACING_3};
        text-align: center;
        box-shadow: {CARD_SHADOW};
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 115px;
    }}

    .rivet-stat-value {{
        font-family: {FONT_MONO};
        font-size: 2.2rem;
        font-weight: 700;
        color: {PRIMARY};
        line-height: 1.1;
    }}

    .rivet-stat-label {{
        font-family: {FONT_SANS};
        font-size: 0.78rem;
        font-weight: 600;
        color: {MUTED_FOREGROUND};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: {SPACING_2};
    }}

    /* -----------------------------------------------------------------------
       Card Containers (Streamlit bordered container + custom class)
       ----------------------------------------------------------------------- */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: {CARD} !important;
        border: 1px solid {BORDER} !important;
        border-radius: {RADIUS_BASE} !important;
        padding: {SPACING_6} !important;
        box-shadow: {CARD_SHADOW} !important;
    }}

    .rivet-card {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_BASE};
        padding: {SPACING_6};
        box-shadow: {CARD_SHADOW};
        margin-bottom: {SPACING_6};
    }}

    .rivet-card-title {{
        font-family: {FONT_SANS};
        font-size: 1.15rem;
        font-weight: 700;
        color: {FOREGROUND};
        margin-bottom: {SPACING_4};
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    /* -----------------------------------------------------------------------
       Buttons (Primary & Secondary)
       ----------------------------------------------------------------------- */
    div.stButton > button[kind="primary"],
    div.stButton > button:first-child {{
        background-color: {PRIMARY} !important;
        color: {PRIMARY_FOREGROUND} !important;
        border-radius: {RADIUS_BASE} !important;
        border: 1px solid {PRIMARY} !important;
        font-family: {FONT_SANS} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem {SPACING_8} !important;
        transition: background-color 0.15s ease, border-color 0.15s ease !important;
        box-shadow: none !important;
    }}

    div.stButton > button[kind="primary"]:hover,
    div.stButton > button:first-child:hover {{
        background-color: {PRIMARY_HOVER} !important;
        border-color: {PRIMARY_HOVER} !important;
        color: {PRIMARY_FOREGROUND} !important;
    }}

    div.stButton > button[kind="secondary"] {{
        background-color: {CARD} !important;
        color: {SECONDARY_FOREGROUND} !important;
        border-radius: {RADIUS_BASE} !important;
        border: 1px solid {BORDER} !important;
        font-family: {FONT_SANS} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem {SPACING_6} !important;
    }}

    div.stButton > button[kind="secondary"]:hover {{
        background-color: {SECONDARY} !important;
        border-color: {INPUT_BORDER} !important;
        color: {FOREGROUND} !important;
    }}

    /* -----------------------------------------------------------------------
       Tabs Styling
       ----------------------------------------------------------------------- */
    div[data-baseweb="tab-list"] {{
        gap: {SPACING_2} !important;
        background-color: transparent !important;
        border-bottom: 1px solid {BORDER} !important;
        padding-bottom: {SPACING_3} !important;
        margin-top: {SPACING_6} !important;
        margin-bottom: {SPACING_6} !important;
    }}

    button[data-baseweb="tab"] {{
        border-radius: {RADIUS_BASE} !important;
        font-family: {FONT_SANS} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: {MUTED_FOREGROUND} !important;
        padding: {SPACING_2} {SPACING_6} !important;
        border: 1px solid transparent !important;
        background-color: transparent !important;
        transition: all 0.15s ease !important;
    }}

    button[data-baseweb="tab"]:hover {{
        color: {FOREGROUND} !important;
        background-color: {MUTED} !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: {ACCENT} !important;
        color: {ACCENT_FOREGROUND} !important;
        border: 1px solid {BORDER} !important;
        font-weight: 700 !important;
    }}

    div[data-baseweb="tab-highlight"] {{
        display: none !important;
    }}

    /* -----------------------------------------------------------------------
       Inputs, Textarea & Selectbox
       ----------------------------------------------------------------------- */
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] > div {{
        border-radius: {RADIUS_INPUT} !important;
        border: 1px solid {INPUT_BORDER} !important;
        background-color: {CARD} !important;
        color: {FOREGROUND} !important;
        font-family: {FONT_SANS} !important;
        font-size: 0.95rem !important;
    }}

    div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within > div {{
        border-color: {RING} !important;
        box-shadow: 0 0 0 2px rgba(51, 91, 73, 0.22) !important;
    }}

    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p {{
        font-family: {FONT_SANS} !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: {FOREGROUND} !important;
        letter-spacing: 0.01em;
        margin-bottom: {SPACING_1};
    }}

    /* -----------------------------------------------------------------------
       Pill Badges for Quality Tiers
       ----------------------------------------------------------------------- */
    .rivet-badge {{
        display: inline-block;
        padding: 0.35rem 1.25rem;
        border-radius: {RADIUS_BADGE};
        font-family: {FONT_SANS};
        font-weight: 700;
        font-size: 0.88rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }}

    .badge-poor {{
        background-color: {CHART_5};
        color: #ffffff;
    }}
    .badge-average {{
        background-color: {CHART_3};
        color: #ffffff;
    }}
    .badge-good {{
        background-color: {CHART_2};
        color: #ffffff;
    }}
    .badge-excellent {{
        background-color: {CHART_1};
        color: #ffffff;
    }}

    /* -----------------------------------------------------------------------
       Soft Warning Card (Human Review)
       ----------------------------------------------------------------------- */
    .rivet-warning-card {{
        background-color: {WARNING_BG};
        border: 1px solid {WARNING_BORDER};
        border-radius: {RADIUS_ALERT};
        padding: {SPACING_3} {SPACING_4};
        color: {WARNING_FOREGROUND};
        font-family: {FONT_SANS};
        font-size: 0.92rem;
        line-height: 1.5;
        margin-top: {SPACING_3};
        margin-bottom: {SPACING_3};
    }}

    .rivet-warning-title {{
        font-weight: 700;
        margin-bottom: 0.2rem;
    }}

    /* -----------------------------------------------------------------------
       Progress Bar
       ----------------------------------------------------------------------- */
    div[data-testid="stProgress"] > div > div > div > div {{
        background-color: {PRIMARY} !important;
        border-radius: {RADIUS_BADGE} !important;
    }}
    div[data-testid="stProgress"] > div > div {{
        background-color: {MUTED} !important;
        border-radius: {RADIUS_BADGE} !important;
        height: 8px !important;
    }}

    /* -----------------------------------------------------------------------
       Dataframe & Tables
       ----------------------------------------------------------------------- */
    div[data-testid="stDataFrame"] {{
        border-radius: {RADIUS_INPUT} !important;
        border: 1px solid {BORDER} !important;
        overflow: hidden !important;
        background-color: {CARD} !important;
    }}

    /* -----------------------------------------------------------------------
       Expanders
       ----------------------------------------------------------------------- */
    div[data-testid="stExpander"] {{
        border-radius: {RADIUS_INPUT} !important;
        border: 1px solid {BORDER} !important;
        background-color: {CARD} !important;
        box-shadow: {CARD_SHADOW} !important;
        margin-bottom: {SPACING_3} !important;
    }}

    div[data-testid="stExpander"] summary {{
        font-family: {FONT_SANS} !important;
        font-weight: 600 !important;
        color: {FOREGROUND} !important;
        font-size: 0.95rem !important;
    }}

    /* -----------------------------------------------------------------------
       Images inside rounded cards
       ----------------------------------------------------------------------- */
    div[data-testid="stImage"] img {{
        border-radius: 1rem;
    }}

    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] {{
        font-family: {FONT_SANS} !important;
        color: {MUTED_FOREGROUND} !important;
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
    }}
    </style>
    """


def inject_css() -> None:
    """Inject custom styles into the Streamlit app."""
    st.markdown(get_css(), unsafe_allow_html=True)
