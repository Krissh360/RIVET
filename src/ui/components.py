"""
src/ui/components.py
--------------------
Reusable layout components for RIVET matching the SPARK design system:
top header, hero, dynamic stat cards, tier badges, and soft alerts.
"""

from __future__ import annotations

import streamlit as st


def render_header() -> None:
    """Render clean top header with circular green logo mark and wordmark."""
    st.markdown(
        """
        <div class="rivet-top-header">
            <div class="rivet-logo-mark">R</div>
            <div class="rivet-wordmark">RIVET</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render centered hero section."""
    st.markdown(
        """
        <div class="rivet-hero">
            <div class="rivet-hero-title">RIVET</div>
            <div class="rivet-hero-subtitle">Rubric-Based Interview Verdict, Evidence and Transcript</div>
            <div class="rivet-hero-headline">
                Every answer, scored <span class="rivet-hero-headline-highlight">with evidence.</span>
            </div>
            <div class="rivet-hero-desc">
                Automated interview response evaluation with rubric criteria scoring,
                transparent confidence metrics, and interpretable feature attribution.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(
    rubric_count: int | None,
    tier_count: int | None,
    question_type_count: int | None,
    test_accuracy: float | None,
) -> None:
    """
    Render row of stat cards. Only cards with valid non-None values are shown.
    """
    cards = []
    if rubric_count is not None:
        cards.append((str(rubric_count), "Rubric Criteria"))
    if tier_count is not None:
        cards.append((str(tier_count), "Quality Tiers"))
    if question_type_count is not None:
        cards.append((str(question_type_count), "Question Types"))
    if test_accuracy is not None:
        cards.append((f"{test_accuracy * 100:.1f}%", "Overall Test Accuracy"))

    if not cards:
        return

    cols = st.columns(len(cards))
    for col, (val, label) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="rivet-stat-card">
                    <div class="rivet-stat-value">{val}</div>
                    <div class="rivet-stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_tier_badge(tier: str) -> str:
    """Return HTML snippet for a pill badge with the appropriate tier color."""
    badge_class = {
        "Poor": "badge-poor",
        "Average": "badge-average",
        "Good": "badge-good",
        "Excellent": "badge-excellent",
    }.get(tier, "badge-good")

    return f'<span class="rivet-badge {badge_class}">{tier}</span>'


def render_review_warning(confidence: float) -> None:
    """Render soft amber card for human review warning."""
    st.markdown(
        f"""
        <div class="rivet-warning-card">
            <div class="rivet-warning-title">Low confidence ({confidence:.0%})</div>
            <div>This prediction falls below the confidence threshold and requires human review.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dataframe(df, use_container_width: bool = True, hide_index: bool = False) -> None:
    """
    Safely render a pandas DataFrame using st.dataframe when pyarrow is present,
    or gracefully fall back to a styled HTML table if pyarrow is not installed.
    """
    try:
        import pyarrow  # noqa: F401
        st.dataframe(df, use_container_width=use_container_width, hide_index=hide_index)
    except (ImportError, ModuleNotFoundError):
        html = df.to_html(classes="rivet-table", index=not hide_index)
        st.markdown(html, unsafe_allow_html=True)
