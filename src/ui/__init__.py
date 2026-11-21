"""
src/ui package
--------------
UI styling, theming, and components for RIVET.
"""

from src.ui.components import (
    render_header,
    render_hero,
    render_stat_cards,
    render_tier_badge,
    render_review_warning,
    render_dataframe,
)
from src.ui.styles import inject_css
from src.ui.charts import plot_probabilities, plot_model_comparison_chart, setup_matplotlib_rc
from src.ui.theme import *
