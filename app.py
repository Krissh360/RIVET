"""
app.py
------
Minimal Streamlit frontend for the RIVET project.
Provides two tabs:
  1. Analyze — enter a response and get prediction, explainability, rubric scores, feedback
  2. Model Performance — view saved evaluation artifacts from outputs/

Run:
    streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import joblib

# ---------------------------------------------------------------------------
# Setup paths — ensure imports work regardless of working directory
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.explain.explain import explain_prediction
from src.explain.rubric_scoring import score_response
from src.explain.feedback import generate_feedback

MODELS_DIR = PROJECT_ROOT / "models" / "baseline"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

LABEL_ORDER = ["Poor", "Average", "Good", "Excellent"]
TIER_COLORS = {
    "Poor": "#e74c3c",
    "Average": "#f39c12",
    "Good": "#2ecc71",
    "Excellent": "#3498db",
}


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


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="RIVET",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 RIVET")
st.caption("Rubric-based Interview Verdict, Evidence and Transcript")

tab_analyze, tab_perf = st.tabs(["📝 Analyze", "📊 Model Performance"])


# ===========================================================================
# TAB 1 — ANALYZE
# ===========================================================================
with tab_analyze:
    model, vectorizer = load_model()

    if model is None:
        st.error(
            "⚠️ No trained model found. Please run:\n\n"
            "```\npython src/training/train_baseline.py\n```"
        )
    else:
        col_input, col_output = st.columns([1, 1])

        with col_input:
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
                height=200,
                placeholder="Paste or type the interview response here…",
            )

            analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

        with col_output:
            if analyze_btn:
                if not response_text.strip():
                    st.warning("Please enter a response to analyze.")
                else:
                    # ----- ML Prediction -----
                    result = explain_prediction(response_text, model, vectorizer)

                    predicted = result["predicted_label"]
                    confidence = result["confidence"]
                    needs_review = result["needs_review"]

                    # Tier badge
                    color = TIER_COLORS.get(predicted, "#888")
                    st.markdown(
                        f"### Predicted Tier: "
                        f"<span style='color:{color}; font-weight:bold'>{predicted}</span>",
                        unsafe_allow_html=True,
                    )

                    # Needs review warning
                    if needs_review:
                        st.warning(
                            f"⚠️ **Low confidence ({confidence:.0%})** — "
                            f"this prediction needs human review."
                        )

                    # Confidence bar
                    st.metric("Confidence", f"{confidence:.1%}")
                    st.progress(confidence)

                    # ----- Class probabilities chart -----
                    st.subheader("Class Probabilities")
                    proba_df = pd.DataFrame({
                        "Tier": LABEL_ORDER,
                        "Probability": [result["probabilities"].get(l, 0) for l in LABEL_ORDER],
                    })
                    st.bar_chart(proba_df.set_index("Tier"))

                    # ----- Rubric criterion scores -----
                    st.subheader("Rubric Criterion Scores")
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
                    st.dataframe(
                        pd.DataFrame(rubric_rows),
                        use_container_width=True,
                        hide_index=True,
                    )

                    # ----- Top contributing words -----
                    st.subheader("Top Contributing Words")
                    if result["top_features"]:
                        feat_df = pd.DataFrame(result["top_features"])
                        feat_df.columns = ["Word / Phrase", "Weight"]
                        feat_df.index = range(1, len(feat_df) + 1)
                        st.dataframe(feat_df, use_container_width=True)
                    else:
                        st.info("No significant features detected (text may be too short).")

                    # ----- Improvement suggestions -----
                    st.subheader("💡 Improvement Suggestions")
                    fb = generate_feedback(predicted, rubric["scores"], question_type)
                    st.info(fb["overall_feedback"])

                    if fb["criterion_feedback"]:
                        for item in fb["criterion_feedback"]:
                            with st.expander(
                                f"📋 {item['criterion'].title()} (score: {item['score']}/10)"
                            ):
                                for sug in item["suggestions"]:
                                    st.markdown(f"- {sug}")
                    else:
                        st.success("All rubric criteria scored above threshold — well done!")


# ===========================================================================
# TAB 2 — MODEL PERFORMANCE
# ===========================================================================
with tab_perf:
    if not OUTPUTS_DIR.exists():
        st.warning(
            "⚠️ No evaluation outputs found. Please run:\n\n"
            "```\npython src/training/evaluate_extended.py\n```"
        )
    else:
        # ----- Confusion Matrix -----
        st.subheader("Confusion Matrix")
        cm_path = OUTPUTS_DIR / "confusion_matrix.png"
        if cm_path.exists():
            st.image(str(cm_path), use_container_width=True)
        else:
            st.info("confusion_matrix.png not found in outputs/.")

        # ----- Classification Report -----
        st.subheader("Classification Report")
        cr_path = OUTPUTS_DIR / "classification_report.csv"
        if cr_path.exists():
            cr_df = pd.read_csv(cr_path, index_col=0)
            st.dataframe(cr_df, use_container_width=True)
        else:
            st.info("classification_report.csv not found in outputs/.")

        # ----- Cross-Validation -----
        st.subheader("5-Fold Cross-Validation")
        cv_path = OUTPUTS_DIR / "cross_validation.csv"
        if cv_path.exists():
            cv_df = pd.read_csv(cv_path)
            st.dataframe(cv_df, use_container_width=True)
            st.metric("Mean CV Accuracy", f"{cv_df['accuracy'].mean():.4f}")
        else:
            st.info("cross_validation.csv not found in outputs/.")

        # ----- Per-question-type -----
        st.subheader("Per-Question-Type Accuracy")
        pt_path = OUTPUTS_DIR / "per_type_accuracy.csv"
        if pt_path.exists():
            pt_df = pd.read_csv(pt_path)
            st.dataframe(pt_df, use_container_width=True)
        else:
            st.info("per_type_accuracy.csv not found in outputs/.")

        # Per-type confusion matrices
        for cat in sorted(["introduction", "why-to-hire"]):
            cm_cat = OUTPUTS_DIR / f"confusion_matrix_{cat}.png"
            if cm_cat.exists():
                st.image(str(cm_cat), caption=f"Confusion Matrix — {cat}", use_container_width=True)

        # ----- Cross-domain -----
        st.subheader("Cross-Domain Evaluation")
        cd_path = OUTPUTS_DIR / "cross_domain.csv"
        if cd_path.exists():
            cd_df = pd.read_csv(cd_path)
            st.dataframe(cd_df, use_container_width=True)
            st.caption(
                "Cross-domain: train on one question type, test on the other. "
                "A large accuracy drop indicates the model is learning question-type-specific patterns."
            )
        else:
            st.info("cross_domain.csv not found in outputs/.")

        # ----- Model comparison -----
        st.subheader("Model Comparison")
        mc_path = OUTPUTS_DIR / "model_comparison.csv"
        if mc_path.exists():
            mc_df = pd.read_csv(mc_path)
            st.dataframe(mc_df, use_container_width=True)
            st.bar_chart(mc_df.set_index("model"))
        else:
            st.info("model_comparison.csv not found in outputs/.")

        # NB confusion matrix
        cm_nb = OUTPUTS_DIR / "confusion_matrix_nb.png"
        if cm_nb.exists():
            st.image(str(cm_nb), caption="Confusion Matrix — Naive Bayes", use_container_width=True)
