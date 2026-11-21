"""
app.py
------
Streamlit frontend for RIVET (Rubric-based Interview Verdict, Evidence and Transcript).
Restyled with the RIVET light theme design system.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Setup paths — ensure imports work regardless of working directory
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.dataset.dataset_config import VALID_CATEGORIES
from src.explain.explain import explain_prediction
from src.explain.feedback import generate_feedback
from src.explain.rubric_scoring import RUBRIC_WEIGHTS, score_response
from src.ui.charts import plot_model_comparison_chart, plot_probabilities
from src.ui.components import (
    render_dataframe,
    render_header,
    render_hero,
    render_review_warning,
    render_stat_cards,
    render_tier_badge,
)
from src.ui.styles import inject_css
from src.ui.theme import LABEL_ORDER

MODELS_DIR = PROJECT_ROOT / "models" / "baseline"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


# ---------------------------------------------------------------------------
# Model loading (cached)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model():
    """Load the saved model and vectorizer. Returns (model, vectorizer) or (None, None)."""
    model_path = MODELS_DIR / "model.pkl"
    vec_path = MODELS_DIR / "vectorizer.pkl"
    if not model_path.exists() or not vec_path.exists():
        return None, None
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    return model, vectorizer


def get_test_accuracy() -> float | None:
    """Read overall test accuracy from classification_report.csv if available."""
    cr_path = OUTPUTS_DIR / "classification_report.csv"
    if not cr_path.exists():
        return None
    try:
        cr_df = pd.read_csv(cr_path, index_col=0)
        if "accuracy" in cr_df.index and "f1-score" in cr_df.columns:
            return float(cr_df.loc["accuracy", "f1-score"])
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# Page configuration & Global Styles
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="RIVET",
    layout="wide",
)

inject_css()

# Top Header & SPARK-style Centered Hero
render_header()
render_hero()

# Dynamic Stat Cards (read from real sources, hidden if unavailable)
model, vectorizer = load_model()

rubric_count = len(RUBRIC_WEIGHTS) if RUBRIC_WEIGHTS else None
tier_count = len(model.classes_) if (model is not None and hasattr(model, "classes_")) else len(LABEL_ORDER)
question_type_count = len(VALID_CATEGORIES) if VALID_CATEGORIES else None
test_accuracy = get_test_accuracy()

render_stat_cards(
    rubric_count=rubric_count,
    tier_count=tier_count,
    question_type_count=question_type_count,
    test_accuracy=test_accuracy,
)

tab_analyze, tab_perf = st.tabs(["Analyze", "Model Performance"])


# ===========================================================================
# TAB 1 — ANALYZE
# ===========================================================================
with tab_analyze:
    if model is None:
        st.error(
            "No trained model found. Please run:\n\n"
            "```\npython src/training/train_baseline.py\n```"
        )
    else:
        col_input, col_output = st.columns([1, 1], gap="large")

        with col_input:
            with st.container(border=True):
                st.markdown('<div class="rivet-card-title">Input Response</div>', unsafe_allow_html=True)
                question_type = st.selectbox(
                    "Question Type",
                    options=["introduction", "why-to-hire"],
                    format_func=lambda x: {
                        "introduction": "Tell me about yourself",
                        "why-to-hire": "Why should we hire you?",
                    }.get(x, x),
                )

                response_text = st.text_area(
                    "Candidate Response",
                    height=220,
                    placeholder="Paste or type the interview response here…",
                )

                analyze_btn = st.button("Analyze", type="primary", use_container_width=True)

        with col_output:
            if analyze_btn:
                if not response_text.strip():
                    st.markdown(
                        '<div class="rivet-warning-card">'
                        '<div class="rivet-warning-title">Input Required</div>'
                        '<div>Please enter a candidate response to analyze.</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    # ML Prediction (logic untouched)
                    result = explain_prediction(response_text, model, vectorizer)

                    predicted = result["predicted_label"]
                    confidence = result["confidence"]
                    needs_review = result["needs_review"]

                    # 1. Prediction & Confidence Card
                    with st.container(border=True):
                        badge_html = render_tier_badge(predicted)
                        st.markdown(
                            f'<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 0.92rem;">'
                            f'<span style="font-weight:700; font-size:1.12rem;">Predicted Quality Tier</span>'
                            f'{badge_html}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        if needs_review:
                            render_review_warning(confidence)

                        st.metric("Confidence Score", f"{confidence:.1%}")
                        st.progress(confidence)

                    # 2. Class Probabilities Card
                    with st.container(border=True):
                        st.markdown('<div class="rivet-card-title">Class Probabilities</div>', unsafe_allow_html=True)
                        fig_proba = plot_probabilities(result["probabilities"])
                        st.pyplot(fig_proba, use_container_width=True)

                    # 3. Rubric Criterion Scores Card
                    rubric = score_response(response_text, question_type)
                    rubric_rows = []
                    for dim in ["content", "relevance", "vocabulary", "structure"]:
                        s = rubric["scores"][dim]
                        rubric_rows.append({
                            "Criterion": dim.title(),
                            "Score (0-10)": s["score"],
                            "Details": s["reason"],
                        })
                    rubric_rows.append({
                        "Criterion": "Overall (weighted)",
                        "Score (0-10)": rubric["overall"],
                        "Details": "0.35×C + 0.25×R + 0.25×V + 0.15×S",
                    })

                    with st.container(border=True):
                        st.markdown('<div class="rivet-card-title">Rubric Criterion Scores</div>', unsafe_allow_html=True)
                        render_dataframe(
                            pd.DataFrame(rubric_rows),
                            use_container_width=True,
                            hide_index=True,
                        )

                    # 4. Top Contributing Words Card
                    with st.container(border=True):
                        st.markdown('<div class="rivet-card-title">Top Contributing Words</div>', unsafe_allow_html=True)
                        if result["top_features"]:
                            feat_df = pd.DataFrame(result["top_features"])
                            feat_df.columns = ["Word / Phrase", "Weight"]
                            feat_df.index = range(1, len(feat_df) + 1)
                            render_dataframe(feat_df, use_container_width=True)
                        else:
                            st.caption("No significant features detected (text may be too short).")

                    # 5. Improvement Suggestions Card
                    fb = generate_feedback(predicted, rubric["scores"], question_type)
                    with st.container(border=True):
                        st.markdown('<div class="rivet-card-title">Improvement Suggestions</div>', unsafe_allow_html=True)
                        st.markdown(
                            f'<div style="background-color: #efeff0; border-radius: 1rem; padding: 0.92rem 1.38rem; margin-bottom: 0.92rem; font-size: 0.92rem; color: #1d1d20;">'
                            f'{fb["overall_feedback"]}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        if fb["criterion_feedback"]:
                            for item in fb["criterion_feedback"]:
                                with st.expander(
                                    f"{item['criterion'].title()} (Score: {item['score']}/10)"
                                ):
                                    for sug in item["suggestions"]:
                                        st.markdown(f"- {sug}")
                        else:
                            st.markdown(
                                '<div style="background-color: #e5ebe8; color: #2e5242; border-radius: 1rem; padding: 0.92rem 1.38rem; font-weight:600;">'
                                'All rubric criteria scored above threshold — strong performance.'
                                '</div>',
                                unsafe_allow_html=True,
                            )


# ===========================================================================
# TAB 2 — MODEL PERFORMANCE
# ===========================================================================
with tab_perf:
    if not OUTPUTS_DIR.exists():
        st.warning(
            "No evaluation outputs found. Please run:\n\n"
            "```\npython src/training/evaluate_extended.py\n```"
        )
    else:
        # Confusion Matrix
        with st.container(border=True):
            st.markdown('<div class="rivet-card-title">Confusion Matrix</div>', unsafe_allow_html=True)
            cm_path = OUTPUTS_DIR / "confusion_matrix.png"
            if cm_path.exists():
                st.image(str(cm_path), use_container_width=True)
            else:
                st.caption("confusion_matrix.png not found in outputs/.")

        # Classification Report
        with st.container(border=True):
            st.markdown('<div class="rivet-card-title">Classification Report</div>', unsafe_allow_html=True)
            cr_path = OUTPUTS_DIR / "classification_report.csv"
            if cr_path.exists():
                cr_df = pd.read_csv(cr_path, index_col=0)
                render_dataframe(cr_df, use_container_width=True)
            else:
                st.caption("classification_report.csv not found in outputs/.")

        # Cross-Validation
        with st.container(border=True):
            st.markdown('<div class="rivet-card-title">5-Fold Cross-Validation</div>', unsafe_allow_html=True)
            cv_path = OUTPUTS_DIR / "cross_validation.csv"
            if cv_path.exists():
                cv_df = pd.read_csv(cv_path)
                mean_acc = cv_df["accuracy"].mean()
                col_metric, col_tbl = st.columns([1, 2], gap="large")
                with col_metric:
                    st.markdown(
                        f"""
                        <div class="rivet-stat-card">
                            <div class="rivet-stat-value">{mean_acc * 100:.2f}%</div>
                            <div class="rivet-stat-label">Mean CV Accuracy</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_tbl:
                    render_dataframe(cv_df, use_container_width=True, hide_index=True)
            else:
                st.caption("cross_validation.csv not found in outputs/.")

        # Per-question-type
        with st.container(border=True):
            st.markdown('<div class="rivet-card-title">Per-Question-Type Accuracy</div>', unsafe_allow_html=True)
            pt_path = OUTPUTS_DIR / "per_type_accuracy.csv"
            if pt_path.exists():
                pt_df = pd.read_csv(pt_path)
                render_dataframe(pt_df, use_container_width=True, hide_index=True)
            else:
                st.caption("per_type_accuracy.csv not found in outputs/.")

            col_cm1, col_cm2 = st.columns(2, gap="medium")
            for idx, cat in enumerate(sorted(["introduction", "why-to-hire"])):
                cm_cat = OUTPUTS_DIR / f"confusion_matrix_{cat}.png"
                target_col = col_cm1 if idx == 0 else col_cm2
                with target_col:
                    if cm_cat.exists():
                        st.image(str(cm_cat), caption=f"Confusion Matrix — {cat}", use_container_width=True)

        # Cross-domain
        with st.container(border=True):
            st.markdown('<div class="rivet-card-title">Cross-Domain Evaluation</div>', unsafe_allow_html=True)
            cd_path = OUTPUTS_DIR / "cross_domain.csv"
            if cd_path.exists():
                cd_df = pd.read_csv(cd_path)
                render_dataframe(cd_df, use_container_width=True, hide_index=True)
                st.caption(
                    "Cross-domain: train on one question type, test on the other. "
                    "A large accuracy drop indicates the model is learning question-type-specific patterns."
                )
            else:
                st.caption("cross_domain.csv not found in outputs/.")

        # Model comparison
        with st.container(border=True):
            st.markdown('<div class="rivet-card-title">Model Comparison</div>', unsafe_allow_html=True)
            mc_path = OUTPUTS_DIR / "model_comparison.csv"
            if mc_path.exists():
                mc_df = pd.read_csv(mc_path)
                render_dataframe(mc_df, use_container_width=True, hide_index=True)
                fig_mc = plot_model_comparison_chart(mc_df)
                st.pyplot(fig_mc, use_container_width=True)
            else:
                st.caption("model_comparison.csv not found in outputs/.")

            cm_nb = OUTPUTS_DIR / "confusion_matrix_nb.png"
            if cm_nb.exists():
                st.image(str(cm_nb), caption="Confusion Matrix — Naive Bayes", use_container_width=True)
