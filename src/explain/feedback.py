"""
feedback.py
-----------
Rule-based improvement suggestions per tier and per low-scoring rubric criterion.
Suggestions are lightly tailored to the question type (introduction vs why-to-hire).

This module works with the rubric scores produced by rubric_scoring.py.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Threshold: a criterion scoring at or below this is "low" and gets feedback
# ---------------------------------------------------------------------------
LOW_SCORE_THRESHOLD = 4  # on the 0-10 scale


# ---------------------------------------------------------------------------
# Per-criterion suggestions, keyed by question type
# ---------------------------------------------------------------------------

_CRITERION_SUGGESTIONS: dict[str, dict[str, list[str]]] = {
    "content": {
        "introduction": [
            "Mention your educational background (degree, university, year).",
            "List 2-3 technical or professional skills relevant to the role.",
            "Briefly describe a project you've worked on and its impact.",
            "Include any notable achievements (hackathons, certifications, awards).",
            "State your career goal to show direction.",
        ],
        "why-to-hire": [
            "Provide concrete evidence of your skills (projects, results, metrics).",
            "Mention specific technologies or tools you are proficient in.",
            "Describe an achievement that demonstrates your value.",
            "Connect your skills directly to what the role requires.",
            "Quantify your impact where possible (e.g., 'reduced processing time by 30%').",
        ],
    },
    "relevance": {
        "introduction": [
            "Focus on your professional background rather than personal hobbies.",
            "Start with who you are professionally (role, field of study).",
            "Make sure every sentence relates to your professional identity.",
        ],
        "why-to-hire": [
            "Directly address why you are a good fit for this specific role.",
            "Avoid generic statements — connect your strengths to employer needs.",
            "Explain what value you bring rather than just listing traits.",
        ],
    },
    "vocabulary": {
        "introduction": [
            "Use complete sentences with proper grammar.",
            "Replace casual words with professional alternatives (e.g., 'utilize' instead of 'use').",
            "Vary your sentence structure to avoid repetition.",
        ],
        "why-to-hire": [
            "Use action verbs (designed, implemented, led, optimized).",
            "Avoid filler words and repetitive phrases.",
            "Demonstrate clear, confident communication.",
        ],
    },
    "structure": {
        "introduction": [
            "Follow the structure: Introduction → Education → Skills → Projects → Goals.",
            "Use transition phrases (e.g., 'Additionally', 'Moving forward').",
            "Aim for at least 3-4 sentences to allow logical flow.",
        ],
        "why-to-hire": [
            "Structure as: Strength → Evidence → Contribution to the company.",
            "Use transition words to connect your points.",
            "End with a clear statement of the value you bring.",
        ],
    },
}


# ---------------------------------------------------------------------------
# Per-tier overall suggestions
# ---------------------------------------------------------------------------

_TIER_SUGGESTIONS: dict[str, dict[str, str]] = {
    "Poor": {
        "introduction": (
            "Your response needs significant improvement. Try to include at least "
            "your name, field of study, and one skill or interest. "
            "Aim for 3+ sentences."
        ),
        "why-to-hire": (
            "Your response needs significant improvement. Provide at least one "
            "concrete reason with evidence (a skill, a project, an experience) "
            "for why you should be hired."
        ),
    },
    "Average": {
        "introduction": (
            "You have a basic foundation. To move to 'Good', add specific projects "
            "or achievements and mention your career goals."
        ),
        "why-to-hire": (
            "You have a basic foundation. To move to 'Good', add specific evidence "
            "(projects, results) and explain how you can contribute to the team."
        ),
    },
    "Good": {
        "introduction": (
            "Solid response! To reach 'Excellent', add quantifiable achievements, "
            "refine your vocabulary, and ensure smooth transitions between sections."
        ),
        "why-to-hire": (
            "Solid response! To reach 'Excellent', include measurable results, "
            "connect your skills more directly to the role, and polish your language."
        ),
    },
    "Excellent": {
        "introduction": (
            "Excellent response! Keep up the comprehensive coverage and professional "
            "communication. Consider tailoring the emphasis based on the specific role."
        ),
        "why-to-hire": (
            "Excellent response! Maintain the evidence-based approach. For even more "
            "impact, tailor specific examples to the company and role you're targeting."
        ),
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_feedback(
    predicted_tier: str,
    rubric_scores: dict,
    question_type: str = "introduction",
) -> dict:
    """
    Generate improvement suggestions based on the predicted tier and rubric scores.

    Parameters
    ----------
    predicted_tier : str
        One of 'Poor', 'Average', 'Good', 'Excellent'.
    rubric_scores : dict
        Output from rubric_scoring.score_response()['scores'], i.e.
        {dimension: {'score': int, 'reason': str}, ...}
    question_type : str
        'introduction' or 'why-to-hire'.

    Returns
    -------
    dict with keys:
        - overall_feedback (str): tier-level feedback message
        - criterion_feedback (list[dict]): per-criterion suggestions for low scores
            each dict: {'criterion': str, 'score': int, 'suggestions': list[str]}
    """
    # Normalize question type
    qt = question_type if question_type in ("introduction", "why-to-hire") else "introduction"

    # Overall tier feedback
    overall_fb = _TIER_SUGGESTIONS.get(predicted_tier, {}).get(
        qt, "Review your response for completeness and clarity."
    )

    # Per-criterion feedback for low-scoring dimensions
    criterion_fb = []
    for criterion, data in rubric_scores.items():
        score = data["score"]
        if score <= LOW_SCORE_THRESHOLD:
            suggestions = _CRITERION_SUGGESTIONS.get(criterion, {}).get(qt, [])
            if suggestions:
                criterion_fb.append({
                    "criterion": criterion,
                    "score": score,
                    "suggestions": suggestions,
                })

    return {
        "overall_feedback": overall_fb,
        "criterion_feedback": criterion_fb,
    }
