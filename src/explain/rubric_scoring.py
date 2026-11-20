"""
rubric_scoring.py
-----------------
Transparent, heuristic-based rubric scoring for interview responses.

Each scoring function maps to one of the four rubric dimensions defined in
docs/scoring_rubric.md. Scores are on a 0-10 scale (more granular than the
1-5 dataset scores) to give the frontend finer resolution.

IMPORTANT: These are simple keyword/pattern heuristics, NOT the ML model's
predictions. They are meant to give a quick, interpretable breakdown that
a student can defend in a viva. The actual model prediction (from TF-IDF +
Logistic Regression) is the authoritative classification.

Rubric dimensions (from docs/scoring_rubric.md):
  1. Content Quality  — amount & quality of professional information
  2. Relevance        — how well the response answers the question
  3. Vocabulary & Communication — language quality, grammar, clarity
  4. Structure         — organization and logical flow

Weights (from docs/scoring_rubric.md):
  overall = 0.35*content + 0.25*relevance + 0.25*vocabulary + 0.15*structure
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Helper: count how many items from a keyword list appear in the text
# ---------------------------------------------------------------------------
def _keyword_hits(text: str, keywords: list[str]) -> int:
    """Count how many keyword phrases appear in the lowered text."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


# ---------------------------------------------------------------------------
# 1. Content Quality Score (0-10)
#    Rubric: measures amount of professional information.
#    Score 1 = almost nothing; Score 5 = education+skills+projects+achievements+goals
#    Heuristic: check for mentions of education, skills, projects, achievements, goals.
# ---------------------------------------------------------------------------

# Keywords signaling each content category from the rubric
_EDUCATION_KW = [
    "student", "university", "college", "degree", "bachelor", "master",
    "engineering", "computer science", "mba", "graduate", "b.tech", "m.tech",
    "btech", "mtech", "diploma", "school", "academic", "semester", "year",
    "pursuing", "completed", "studied", "major", "minor", "b.e", "m.e",
    "bsc", "msc", "phd", "education",
]

_SKILLS_KW = [
    "python", "java", "javascript", "c++", "sql", "html", "css", "react",
    "node", "machine learning", "deep learning", "data science", "data analysis",
    "web development", "cloud", "aws", "azure", "docker", "git", "linux",
    "tensorflow", "pytorch", "nlp", "api", "database", "excel", "tableau",
    "power bi", "communication", "leadership", "teamwork", "problem solving",
    "analytical", "flutter", "android", "ios", "devops", "agile", "scrum",
    "spring", "django", "flask", "angular", "vue", "typescript", "kubernetes",
    "skill", "proficient", "experienced",
]

_PROJECTS_KW = [
    "project", "built", "developed", "created", "designed", "implemented",
    "application", "app", "system", "tool", "website", "platform", "portfolio",
    "prototype", "capstone", "thesis", "research paper", "publication",
]

_ACHIEVEMENTS_KW = [
    "hackathon", "competition", "award", "winner", "certified", "certification",
    "achievement", "medal", "rank", "topper", "scholarship", "recognition",
    "published", "patent", "contributed", "open source", "volunteer",
    "internship", "intern", "experience", "worked at", "company",
]

_GOALS_KW = [
    "goal", "aim", "aspire", "career", "future", "plan", "vision", "dream",
    "become", "contribute", "grow", "pursue", "long-term", "short-term",
    "objective", "ambition", "looking forward", "passionate about",
]


def score_content(text: str) -> tuple[int, str]:
    """
    Score content quality (0-10).

    Maps to rubric §1 "Content Quality Score":
      - Score 1-2: very little useful information
      - Score 3-4: basic info (education OR interests)
      - Score 5-6: moderate (education + some skills)
      - Score 7-8: strong (education + skills + projects)
      - Score 9-10: comprehensive (education + skills + projects + achievements + goals)
    """
    categories_found = 0
    details = []

    edu = _keyword_hits(text, _EDUCATION_KW)
    if edu > 0:
        categories_found += 1
        details.append("education")

    skills = _keyword_hits(text, _SKILLS_KW)
    if skills > 0:
        categories_found += 1
        details.append("skills")

    proj = _keyword_hits(text, _PROJECTS_KW)
    if proj > 0:
        categories_found += 1
        details.append("projects")

    ach = _keyword_hits(text, _ACHIEVEMENTS_KW)
    if ach > 0:
        categories_found += 1
        details.append("achievements")

    goals = _keyword_hits(text, _GOALS_KW)
    if goals > 0:
        categories_found += 1
        details.append("goals")

    # Map 0-5 categories to 0-10 score
    score = min(categories_found * 2, 10)

    # Bonus: if many keyword hits in total, nudge score up
    total_hits = edu + skills + proj + ach + goals
    if total_hits >= 8 and score < 10:
        score = min(score + 1, 10)

    reason = f"Detected: {', '.join(details) if details else 'none'} ({total_hits} keyword hits)"
    return score, reason


# ---------------------------------------------------------------------------
# 2. Relevance Score (0-10)
#    Rubric §2: measures how well the response answers the question.
#    Heuristic: check for self-introduction patterns, professional keywords,
#    and penalize off-topic content.
# ---------------------------------------------------------------------------

_PROFESSIONAL_INTRO_KW = [
    "i am", "my name", "i have", "i work", "i currently", "my background",
    "my experience", "i completed", "i graduated", "i specialize",
    "i am a", "i'm a", "myself", "i hold", "i bring",
    "my role", "i was", "in my career", "i've been",
]

_OFFTOPIC_KW = [
    "cricket", "movie", "food", "weather", "politics", "i don't know",
    "no idea", "nothing much", "not sure what to say",
]


def score_relevance(text: str, question_type: str = "introduction") -> tuple[int, str]:
    """
    Score relevance (0-10).

    Maps to rubric §2 "Relevance Score":
      - Score 1-2: completely off-topic
      - Score 3-4: mostly irrelevant
      - Score 5-6: partially relevant
      - Score 7-8: relevant professional background
      - Score 9-10: highly relevant, directly answers the question

    Parameters
    ----------
    text : str
        The response text.
    question_type : str
        'introduction' or 'why-to-hire'. Affects which keywords matter most.
    """
    text_lower = text.lower()
    word_count = len(text.split())

    # Off-topic penalty
    offtopic = _keyword_hits(text, _OFFTOPIC_KW)
    prof_intro = _keyword_hits(text, _PROFESSIONAL_INTRO_KW)
    content_hits = _keyword_hits(text, _EDUCATION_KW + _SKILLS_KW + _PROJECTS_KW)

    # Question-type-specific relevance boost
    if question_type == "why-to-hire":
        hire_kw = ["hire", "contribute", "value", "strength", "bring",
                   "benefit", "fit", "role", "position", "team", "company",
                   "organization", "employer"]
        hire_hits = _keyword_hits(text, hire_kw)
        content_hits += hire_hits

    # Very short responses tend to be less relevant
    length_factor = min(word_count / 30, 1.0)  # ramp up to 30 words

    # Base score from professional content signals
    if offtopic > 1 and prof_intro == 0:
        score = 1
    elif content_hits == 0 and prof_intro == 0:
        score = 2
    elif content_hits <= 1:
        score = 4
    elif content_hits <= 3:
        score = 6
    elif content_hits <= 6:
        score = 8
    else:
        score = 10

    # Apply length factor (very short = less relevant)
    score = max(1, int(score * max(length_factor, 0.3)))

    reason = (
        f"Professional signals: {prof_intro}, content keywords: {content_hits}, "
        f"off-topic: {offtopic}, word count: {word_count}"
    )
    return min(score, 10), reason


# ---------------------------------------------------------------------------
# 3. Vocabulary & Communication Score (0-10)
#    Rubric §3: language quality, grammar, clarity, professionalism.
#    Heuristic: average word length, sentence count, type-token ratio,
#    and presence of professional language markers.
# ---------------------------------------------------------------------------

def score_vocabulary(text: str) -> tuple[int, str]:
    """
    Score vocabulary and communication quality (0-10).

    Maps to rubric §3 "Vocabulary & Communication Score":
      - Score 1-2: very poor communication
      - Score 3-4: weak communication with grammar issues
      - Score 5-6: understandable but basic
      - Score 7-8: clear and professional
      - Score 9-10: highly polished, fluent communication
    """
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0, "Empty response"

    # Average word length — longer words often indicate more sophisticated vocabulary
    avg_word_len = sum(len(w) for w in words) / word_count

    # Sentence count (approximate)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = max(len(sentences), 1)

    # Type-token ratio (vocabulary diversity)
    unique_words = set(w.lower() for w in words)
    ttr = len(unique_words) / word_count if word_count > 0 else 0

    # Professional language markers
    prof_markers = [
        "furthermore", "additionally", "moreover", "consequently",
        "demonstrate", "proficient", "expertise", "comprehensive",
        "leverage", "implement", "collaborate", "initiative",
        "effectively", "efficiently", "strategic", "analytical",
        "passionate", "dedicated", "innovative", "motivated",
    ]
    prof_count = _keyword_hits(text, prof_markers)

    # Scoring logic
    score = 5  # start at "understandable but basic"

    # Word length bonus (avg > 4.5 chars is above simple vocabulary)
    if avg_word_len >= 5.0:
        score += 1
    elif avg_word_len < 3.5:
        score -= 1

    # Vocabulary diversity bonus
    if ttr >= 0.7:
        score += 1
    elif ttr < 0.4:
        score -= 1

    # Length/completeness factor
    if word_count >= 60:
        score += 1
    elif word_count < 15:
        score -= 2

    # Professional language bonus
    if prof_count >= 3:
        score += 2
    elif prof_count >= 1:
        score += 1

    # Multi-sentence bonus
    if sentence_count >= 3:
        score += 1

    score = max(1, min(score, 10))
    reason = (
        f"Avg word length: {avg_word_len:.1f}, unique/total ratio: {ttr:.2f}, "
        f"sentences: {sentence_count}, professional markers: {prof_count}"
    )
    return score, reason


# ---------------------------------------------------------------------------
# 4. Structure Score (0-10)
#    Rubric §4: organization and logical flow.
#    Preferred structure: Introduction → Education → Skills → Projects → Goals
#    Heuristic: check for multi-sentence structure, presence of sections
#    in roughly the right order.
# ---------------------------------------------------------------------------

def score_structure(text: str) -> tuple[int, str]:
    """
    Score structural organization (0-10).

    Maps to rubric §4 "Structure Score":
      - Score 1-2: no structure
      - Score 3-4: weak organization
      - Score 5-6: some logical flow
      - Score 7-8: well-organized answer
      - Score 9-10: excellent structure with smooth transitions
    """
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0, "Empty response"

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = len(sentences)

    # Check for expected structural sections (order matters)
    # Rubric preferred flow: Introduction → Education → Skills → Projects → Goals
    section_patterns = [
        ("introduction", ["my name", "i am", "i'm", "myself", "hello", "hi"]),
        ("education", _EDUCATION_KW[:10]),
        ("skills", _SKILLS_KW[:15]),
        ("projects", _PROJECTS_KW[:8]),
        ("goals", _GOALS_KW[:8]),
    ]

    sections_found = []
    for section_name, keywords in section_patterns:
        if _keyword_hits(text, keywords) > 0:
            sections_found.append(section_name)

    # Transition words indicate good flow
    transitions = [
        "currently", "additionally", "moreover", "furthermore", "also",
        "in addition", "apart from", "besides", "moving forward",
        "looking ahead", "in the future", "my goal", "i aim",
        "as for", "with regard to", "when it comes to",
    ]
    transition_count = _keyword_hits(text, transitions)

    # Scoring
    score = 3  # start at "some structure"

    # Number of sections found
    if len(sections_found) >= 4:
        score += 3
    elif len(sections_found) >= 3:
        score += 2
    elif len(sections_found) >= 2:
        score += 1

    # Multi-sentence = more organized
    if sentence_count >= 5:
        score += 2
    elif sentence_count >= 3:
        score += 1
    elif sentence_count <= 1:
        score -= 2

    # Transition words signal smooth flow
    if transition_count >= 3:
        score += 1
    elif transition_count >= 1:
        score += 1

    # Very short = no room for structure
    if word_count < 15:
        score = min(score, 3)

    score = max(1, min(score, 10))
    reason = (
        f"Sections found: {', '.join(sections_found) if sections_found else 'none'}, "
        f"sentences: {sentence_count}, transitions: {transition_count}"
    )
    return score, reason


# ---------------------------------------------------------------------------
# Combined rubric scoring
# ---------------------------------------------------------------------------

# Weights from docs/scoring_rubric.md §"Overall Score Formula"
RUBRIC_WEIGHTS = {
    "content":    0.35,
    "relevance":  0.25,
    "vocabulary": 0.25,
    "structure":  0.15,
}


def score_response(text: str, question_type: str = "introduction") -> dict:
    """
    Compute all four rubric dimension scores and overall weighted score.

    Parameters
    ----------
    text : str
        The interview response text.
    question_type : str
        'introduction' or 'why-to-hire'.

    Returns
    -------
    dict with keys:
        - scores: dict of dimension -> {'score': int (0-10), 'reason': str}
        - overall: float (0-10 weighted)
        - weights: dict of dimension -> weight (from rubric)
    """
    content_score, content_reason = score_content(text)
    relevance_score, relevance_reason = score_relevance(text, question_type)
    vocab_score, vocab_reason = score_vocabulary(text)
    struct_score, struct_reason = score_structure(text)

    scores = {
        "content":    {"score": content_score,    "reason": content_reason},
        "relevance":  {"score": relevance_score,  "reason": relevance_reason},
        "vocabulary": {"score": vocab_score,      "reason": vocab_reason},
        "structure":  {"score": struct_score,     "reason": struct_reason},
    }

    overall = round(
        RUBRIC_WEIGHTS["content"]    * content_score +
        RUBRIC_WEIGHTS["relevance"]  * relevance_score +
        RUBRIC_WEIGHTS["vocabulary"] * vocab_score +
        RUBRIC_WEIGHTS["structure"]  * struct_score,
        2,
    )

    return {
        "scores": scores,
        "overall": overall,
        "weights": RUBRIC_WEIGHTS,
    }
