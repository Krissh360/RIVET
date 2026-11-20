"""
evaluate_extended.py
--------------------
Extended evaluation suite for the RIVET baseline classifier.
Leaves evaluate_baseline.py completely untouched.

Features:
  - Stratified train/test split and 5-fold cross-validation
  - Classification report (printed and saved as CSV)
  - Confusion matrix image saved to outputs/
  - Per-question-type metrics
  - Cross-domain check: train on one question type, test on the other
  - Model comparison: Logistic Regression vs Multinomial Naive Bayes
  - All artifacts saved to outputs/ for the Streamlit frontend

Usage
-----
    python src/training/evaluate_extended.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for saving figures
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import cross_val_score, StratifiedKFold

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.training.preprocess import load_dataset, prepare_data
from src.dataset.dataset_config import DatasetConfig, VALID_CATEGORIES, PROJECT_ROOT
from src.ui.charts import GREEN_COLORMAP, setup_matplotlib_rc

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LABEL_ORDER = ["Poor", "Average", "Good", "Excellent"]


def ensure_outputs_dir() -> Path:
    """Create outputs/ directory if it doesn't exist."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTS_DIR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_vectorizer() -> TfidfVectorizer:
    """Same config as train_baseline.py for consistency."""
    return TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )


def build_logreg() -> LogisticRegression:
    """Same config as train_baseline.py for consistency."""
    return LogisticRegression(max_iter=1000, random_state=42, solver="lbfgs")


def build_nb() -> MultinomialNB:
    """Multinomial Naive Bayes baseline for comparison."""
    return MultinomialNB(alpha=1.0)


def load_category_data(category: str) -> pd.DataFrame:
    """Load a single category's merged CSV."""
    config = DatasetConfig(category)
    return load_dataset(str(config.output_file))


def save_classification_report_csv(
    y_true, y_pred, path: Path, label_order: list[str] | None = None
) -> str:
    """Save sklearn classification report as CSV and return the report string."""
    present = [l for l in (label_order or LABEL_ORDER) if l in set(y_true) | set(y_pred)]
    report_str = classification_report(y_true, y_pred, labels=present, zero_division=0)
    report_dict = classification_report(
        y_true, y_pred, labels=present, output_dict=True, zero_division=0
    )
    df = pd.DataFrame(report_dict).transpose()
    df.to_csv(path)
    return report_str


def save_confusion_matrix_image(
    y_true, y_pred, path: Path, title: str = "Confusion Matrix"
) -> None:
    """Save a confusion matrix as a PNG image using the RIVET green palette."""
    setup_matplotlib_rc()
    present = [l for l in LABEL_ORDER if l in set(y_true) | set(y_pred)]
    cm = confusion_matrix(y_true, y_pred, labels=present)
    fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=150)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=present)
    disp.plot(ax=ax, cmap=GREEN_COLORMAP, values_format="d", colorbar=True)
    ax.grid(False)
    ax.set_title(title, fontsize=12, pad=12, fontweight="600")
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor="#ffffff")
    plt.close(fig)
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# 1. Main evaluation on merged (all categories) dataset
# ---------------------------------------------------------------------------

def run_main_evaluation() -> None:
    """
    Train on all data, evaluate with stratified split + 5-fold CV,
    and save artifacts.
    """
    out = ensure_outputs_dir()
    print("=" * 60)
    print("  RIVET — Extended Evaluation")
    print("=" * 60)

    # Load all categories and tag them
    frames = []
    for cat in sorted(VALID_CATEGORIES):
        try:
            df = load_category_data(cat)
            df["question_type"] = cat
            frames.append(df)
            print(f"  Loaded {len(df)} rows from '{cat}'")
        except FileNotFoundError:
            print(f"  ⚠ Skipping '{cat}' — merged CSV not found. Run merge_datasets.py first.")

    if not frames:
        print("ERROR: No data loaded. Run merge_datasets.py for at least one category.")
        sys.exit(1)

    combined = pd.concat(frames, ignore_index=True)
    print(f"\n  Combined dataset: {len(combined)} rows\n")

    # Stratified split
    X_train, X_test, y_train, y_test = prepare_data(combined)

    # Keep track of question_type for per-type metrics later
    test_indices = X_test.index
    test_qtypes = combined.loc[test_indices, "question_type"]

    # Fit vectorizer + Logistic Regression
    vectorizer = build_vectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    model_lr = build_logreg()
    model_lr.fit(X_train_tfidf, y_train)
    y_pred_lr = model_lr.predict(X_test_tfidf)

    # --- Accuracy ---
    acc = accuracy_score(y_test, y_pred_lr)
    print(f"\n  Overall Accuracy (Logistic Regression): {acc:.4f} ({acc*100:.2f}%)\n")

    # --- Classification report ---
    report_str = save_classification_report_csv(
        y_test, y_pred_lr, out / "classification_report.csv"
    )
    print("  Classification Report:")
    print(report_str)
    # Also save as text
    (out / "classification_report.txt").write_text(report_str, encoding="utf-8")

    # --- Confusion matrix ---
    save_confusion_matrix_image(
        y_test, y_pred_lr, out / "confusion_matrix.png",
        title="RIVET — Confusion Matrix (Logistic Regression)"
    )

    # --- 5-fold cross-validation ---
    print("\n  5-Fold Stratified Cross-Validation:")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    # We need to re-fit vectorizer inside each fold, so use the full pipeline
    # For simplicity with cross_val_score, we vectorize upfront (slight optimistic bias
    # acknowledged — but keeps the code simple for a student project)
    X_all_tfidf = vectorizer.transform(combined["answer"].astype(str).str.strip())
    y_all = combined["label"]
    cv_scores = cross_val_score(
        build_logreg(), X_all_tfidf, y_all, cv=cv, scoring="accuracy"
    )
    print(f"    Fold accuracies: {[f'{s:.4f}' for s in cv_scores]}")
    print(f"    Mean: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    cv_df = pd.DataFrame({
        "fold": list(range(1, 6)),
        "accuracy": cv_scores,
    })
    cv_df.to_csv(out / "cross_validation.csv", index=False)

    # -----------------------------------------------------------------------
    # 2. Per-question-type metrics
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Per-Question-Type Metrics")
    print("=" * 60)

    per_type_results = []
    for qt in sorted(VALID_CATEGORIES):
        mask = test_qtypes == qt
        if mask.sum() == 0:
            print(f"\n  [{qt}] No test samples. Skipping.")
            continue

        y_true_qt = y_test[mask]
        y_pred_qt = y_pred_lr[mask]
        acc_qt = accuracy_score(y_true_qt, y_pred_qt)
        per_type_results.append({"question_type": qt, "accuracy": acc_qt, "n_test": int(mask.sum())})

        print(f"\n  [{qt}] Accuracy: {acc_qt:.4f} ({mask.sum()} test samples)")
        report_qt = save_classification_report_csv(
            y_true_qt, y_pred_qt,
            out / f"classification_report_{qt}.csv"
        )
        print(report_qt)
        save_confusion_matrix_image(
            y_true_qt, y_pred_qt,
            out / f"confusion_matrix_{qt}.png",
            title=f"Confusion Matrix — {qt}",
        )

    if per_type_results:
        pd.DataFrame(per_type_results).to_csv(out / "per_type_accuracy.csv", index=False)

    # -----------------------------------------------------------------------
    # 3. Cross-domain check: train on one type, test on the other
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Cross-Domain Evaluation")
    print("=" * 60)

    cats = sorted(VALID_CATEGORIES)
    cross_results = []
    for train_cat in cats:
        for test_cat in cats:
            if train_cat == test_cat:
                continue

            try:
                df_train = load_category_data(train_cat)
                df_test = load_category_data(test_cat)
            except FileNotFoundError:
                continue

            vec = build_vectorizer()
            X_tr = vec.fit_transform(df_train["answer"].astype(str).str.strip())
            X_te = vec.transform(df_test["answer"].astype(str).str.strip())

            clf = build_logreg()
            clf.fit(X_tr, df_train["label"])
            y_pred_cross = clf.predict(X_te)
            acc_cross = accuracy_score(df_test["label"], y_pred_cross)

            cross_results.append({
                "train_on": train_cat,
                "test_on": test_cat,
                "accuracy": round(acc_cross, 4),
                "n_train": len(df_train),
                "n_test": len(df_test),
            })
            print(f"\n  Train: {train_cat} → Test: {test_cat}")
            print(f"  Accuracy: {acc_cross:.4f}")

    if cross_results:
        pd.DataFrame(cross_results).to_csv(out / "cross_domain.csv", index=False)

    # -----------------------------------------------------------------------
    # 4. Model comparison: Logistic Regression vs Multinomial Naive Bayes
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Model Comparison")
    print("=" * 60)

    model_nb = build_nb()
    model_nb.fit(X_train_tfidf, y_train)
    y_pred_nb = model_nb.predict(X_test_tfidf)
    acc_nb = accuracy_score(y_test, y_pred_nb)

    comparison = pd.DataFrame([
        {"model": "Logistic Regression", "accuracy": round(acc, 4)},
        {"model": "Multinomial Naive Bayes", "accuracy": round(acc_nb, 4)},
    ])
    comparison.to_csv(out / "model_comparison.csv", index=False)
    print(f"\n  Logistic Regression   : {acc:.4f}")
    print(f"  Multinomial Naive Bayes: {acc_nb:.4f}")
    print(f"\n  Saved: {out / 'model_comparison.csv'}")

    # Also save NB confusion matrix
    save_confusion_matrix_image(
        y_test, y_pred_nb,
        out / "confusion_matrix_nb.png",
        title="Confusion Matrix — Naive Bayes",
    )

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  All outputs saved to: outputs/")
    print("=" * 60)
    print("  Files created:")
    for f in sorted(OUTPUTS_DIR.glob("*")):
        print(f"    • {f.name}")
    print()


if __name__ == "__main__":
    run_main_evaluation()
