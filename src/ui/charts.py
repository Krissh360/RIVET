"""
src/ui/charts.py
----------------
Matplotlib rcParams configuration, color maps, and chart rendering helpers
matching the RIVET design system.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import pandas as pd

from src.ui.theme import (
    PRIMARY,
    FOREGROUND,
    MUTED_FOREGROUND,
    BORDER,
    MUTED,
    CARD,
    CHART_1,
    CHART_2,
    CHART_PALETTE,
    TIER_COLORS,
)

# Sequential green colormap derived from primary color #335b49
GREEN_COLORMAP = LinearSegmentedColormap.from_list(
    "rivet_green",
    ["#fbfbfb", "#e5ebe8", "#8cb5a1", "#335b49", "#1b3329"],
    N=256,
)


def setup_matplotlib_rc() -> None:
    """Set global matplotlib rcParams to adhere to RIVET design tokens."""
    # Register local TTF font files if present
    fonts_dir = Path(__file__).resolve().parents[2] / "static" / "fonts"
    for ttf_file in fonts_dir.glob("*.ttf"):
        try:
            fm.fontManager.addfont(str(ttf_file))
        except Exception:
            pass

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Raleway", "system-ui", "DejaVu Sans", "sans-serif"],
        "figure.facecolor": CARD,
        "figure.edgecolor": "none",
        "axes.facecolor": CARD,
        "axes.edgecolor": BORDER,
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.labelcolor": FOREGROUND,
        "axes.labelsize": 10,
        "axes.labelweight": "600",
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": MUTED,
        "grid.linestyle": "--",
        "grid.linewidth": 0.8,
        "grid.alpha": 0.8,
        "xtick.color": MUTED_FOREGROUND,
        "xtick.labelsize": 9.5,
        "ytick.color": MUTED_FOREGROUND,
        "ytick.labelsize": 9.5,
        "text.color": FOREGROUND,
    })


def plot_probabilities(proba_dict: dict[str, float]) -> matplotlib.figure.Figure:
    """
    Render horizontal bar chart for class probabilities using tier colors.
    """
    setup_matplotlib_rc()
    tiers = ["Poor", "Average", "Good", "Excellent"]
    probs = [proba_dict.get(t, 0.0) * 100 for t in tiers]
    colors = [TIER_COLORS[t] for t in tiers]

    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=130)
    bars = ax.barh(tiers, probs, color=colors, height=0.52, edgecolor="none")

    max_prob = max(probs) if probs else 100
    ax.set_xlim(0, max(max_prob * 1.25, 15))
    ax.xaxis.set_major_formatter(ticker.PercentFormatter(100, decimals=0))
    ax.set_xlabel("Probability (%)", labelpad=8)
    ax.invert_yaxis()

    # Percentage data labels in Roboto Mono
    for bar, val in zip(bars, probs):
        if val > 0:
            ax.text(
                bar.get_width() + 1.2,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%",
                va="center",
                ha="left",
                fontfamily="Roboto Mono",
                fontsize=9.5,
                fontweight="600",
                color=FOREGROUND,
            )

    fig.tight_layout()
    return fig


def plot_model_comparison_chart(mc_df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Render bar chart for model accuracy comparison.
    """
    setup_matplotlib_rc()
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=130)

    models = mc_df["model"].tolist()
    accs = [val * 100 for val in mc_df["accuracy"]]
    colors = [CHART_1, CHART_2][:len(models)]

    bars = ax.bar(models, accs, color=colors, width=0.45, edgecolor="none")
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(100, decimals=0))
    ax.set_ylabel("Accuracy (%)", labelpad=8)

    for bar, val in zip(bars, accs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2.0,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontfamily="Roboto Mono",
            fontsize=9.5,
            fontweight="600",
            color=FOREGROUND,
        )

    fig.tight_layout()
    return fig
