"""
explain.py
----------
Explainability module for the RIVET baseline classifier.

Given a text response, identifies the top words/phrases (TF-IDF features)
that push the prediction toward the predicted tier, using the logistic
regression coefficients and the TF-IDF feature names.

This provides transparent, model-intrinsic evidence for each prediction —
no black-box post-hoc methods are needed because Logistic Regression is
a linear model with directly interpretable coefficients.

Usage
-----
    from src.explain.explain import explain_prediction
    result = explain_prediction("I am a CS student with ML projects.", model, vectorizer)
"""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def explain_prediction(
    text: str,
    model: LogisticRegression,
    vectorizer: TfidfVectorizer,
    top_n: int = 5,
) -> dict:
    """
    Explain a single prediction by identifying the top contributing features.

    How it works
    ------------
    For a linear model, the prediction score for class c is:
        score_c = sum( tfidf_weight_i * coefficient_c_i )

    We compute the per-feature contribution for the *predicted* class:
        contribution_i = tfidf_weight_i * coefficient_predicted_i

    The features with the largest positive contributions are the ones
    "pushing" the prediction toward the predicted tier.

    Parameters
    ----------
    text : str
        The interview response text to explain.
    model : LogisticRegression
        Trained logistic regression classifier.
    vectorizer : TfidfVectorizer
        Fitted TF-IDF vectorizer.
    top_n : int
        Number of top contributing features to return (default: 5).

    Returns
    -------
    dict with keys:
        - predicted_label (str): the predicted tier
        - top_features (list[dict]): each dict has 'feature' (str) and 'weight' (float)
        - probabilities (dict): class name -> probability
        - confidence (float): probability of the predicted class
        - needs_review (bool): True if confidence < 0.60
    """
    # Vectorize the input text
    tfidf_vector = vectorizer.transform([text])

    # Get prediction and probabilities
    predicted_label = model.predict(tfidf_vector)[0]
    proba = model.predict_proba(tfidf_vector)[0]

    # Build class -> probability mapping
    class_probabilities = {
        cls: round(float(p), 4) for cls, p in zip(model.classes_, proba)
    }
    confidence = float(class_probabilities[predicted_label])

    # --- Feature contribution analysis ---
    # Find the index of the predicted class in model.classes_
    predicted_idx = list(model.classes_).index(predicted_label)

    # Coefficients for the predicted class (shape: n_features)
    coefficients = model.coef_[predicted_idx]

    # TF-IDF values for this text (sparse row -> dense array)
    tfidf_values = tfidf_vector.toarray().flatten()

    # Per-feature contribution = tfidf_value * coefficient
    contributions = tfidf_values * coefficients

    # Feature names from the vectorizer
    feature_names = vectorizer.get_feature_names_out()

    # Get indices of top-N positive contributions (descending)
    # We only care about features that are actually present (tfidf > 0)
    nonzero_mask = tfidf_values > 0
    if nonzero_mask.sum() == 0:
        top_features = []
    else:
        # Among nonzero features, sort by contribution descending
        nonzero_indices = np.where(nonzero_mask)[0]
        nonzero_contributions = contributions[nonzero_indices]
        sorted_order = np.argsort(nonzero_contributions)[::-1]
        top_indices = nonzero_indices[sorted_order[:top_n]]

        top_features = [
            {
                "feature": feature_names[i],
                "weight": round(float(contributions[i]), 4),
            }
            for i in top_indices
        ]

    return {
        "predicted_label": predicted_label,
        "top_features": top_features,
        "probabilities": class_probabilities,
        "confidence": confidence,
        "needs_review": confidence < 0.60,
    }


def format_explanation(result: dict) -> str:
    """
    Format an explanation result as a human-readable string.

    Parameters
    ----------
    result : dict
        Output from explain_prediction().

    Returns
    -------
    str
        Formatted multi-line explanation.
    """
    lines = []
    lines.append(f"Predicted Tier : {result['predicted_label']}")
    lines.append(f"Confidence     : {result['confidence']:.1%}")

    if result["needs_review"]:
        lines.append("⚠  LOW CONFIDENCE — this prediction needs human review.")

    lines.append("\nClass Probabilities:")
    for cls in ["Poor", "Average", "Good", "Excellent"]:
        p = result["probabilities"].get(cls, 0)
        bar = "█" * int(p * 20)
        lines.append(f"  {cls:<10} {p:.1%}  {bar}")

    lines.append(f"\nTop {len(result['top_features'])} Contributing Words/Phrases:")
    for i, feat in enumerate(result["top_features"], 1):
        lines.append(f"  {i}. \"{feat['feature']}\" (weight: {feat['weight']:+.4f})")

    return "\n".join(lines)
