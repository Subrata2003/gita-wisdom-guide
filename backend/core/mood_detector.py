"""
Mood detector for Gita Wisdom Guide.

Analyses the seeker's query text and returns the dominant emotional state
so Krishna can adapt his tone accordingly.

Detection is purely lexical (keyword scoring) — fast, offline, no LLM call needed.
"""

from enum import Enum
from typing import Tuple


class Mood(str, Enum):
    GRIEF      = "grief"
    ANGER      = "anger"
    ANXIETY    = "anxiety"
    CONFUSION  = "confusion"
    DESPAIR    = "despair"
    LONGING    = "longing"
    CURIOSITY  = "curiosity"
    NEUTRAL    = "neutral"


# ── Keyword / phrase signals per mood ─────────────────────────────────────────
# Each phrase scores 1 point; longer phrases are listed first so they are
# matched before their constituent words. Match is case-insensitive substring.

_SIGNALS: dict[Mood, list[str]] = {
    Mood.GRIEF: [
        "passed away", "lost someone", "can't stop crying", "heartbroken",
        "grief", "grieving", "mourning", "mourn", "bereavement", "bereaved",
        "loss", "losing", "died", "death", "miss them", "devastated",
        "sad", "sadness", "tears", "crying", "weeping", "broken heart",
        "hurt so much", "deep pain",
    ],
    Mood.ANGER: [
        "so angry", "filled with rage", "can't forgive", "burning with",
        "anger", "rage", "furious", "resentment", "resentful", "bitter",
        "bitterness", "betrayed", "betrayal", "frustrated", "frustration",
        "irritated", "jealous", "jealousy", "envy", "envious",
        "unfair", "injustice", "hatred", "hate", "revenge",
    ],
    Mood.ANXIETY: [
        "can't stop worrying", "what if", "scared of the future",
        "anxiety", "anxious", "panic", "panicking", "overwhelmed",
        "stressed out", "stress", "worry", "worried", "worrying",
        "afraid", "fearful", "fear", "nervous", "dread", "dreading",
        "overthinking", "uncertain", "uncertainty", "apprehensive",
        "uneasy", "on edge",
    ],
    Mood.CONFUSION: [
        "don't know what to do", "have no idea", "which path",
        "so confused", "lost my way", "no direction", "torn between",
        "confused", "confusion", "purpose", "meaning", "why am i",
        "what should i", "how should i", "dilemma", "crossroads",
        "unsure", "doubt", "doubting", "unclear", "lost",
    ],
    Mood.DESPAIR: [
        "giving up", "no point", "nothing matters", "can't go on",
        "feel hopeless", "feel worthless", "feel empty", "lost all hope",
        "despair", "desperate", "hopeless", "hopelessness",
        "worthless", "meaningless", "pointless", "empty", "emptiness",
        "void", "failed", "complete failure", "dark place",
    ],
    Mood.LONGING: [
        "feel so alone", "no one understands", "longing for",
        "lonely", "loneliness", "alone", "isolated", "disconnected",
        "rejected", "rejection", "unwanted", "unloved", "miss",
        "missing", "yearning", "yearn", "belonging", "connection",
    ],
    Mood.CURIOSITY: [
        "what does the gita say", "tell me about", "explain to me",
        "how does", "what is", "what are", "what was",
        "curious", "curious about", "learn about", "understand",
        "philosophy", "meaning of", "concept", "teach me",
        "describe", "who is", "what happens",
    ],
}

# Minimum total score needed to declare a non-neutral mood
_THRESHOLD = 1


def detect_mood(query: str) -> Tuple[Mood, int]:
    """
    Returns (dominant_mood, score).
    Score is the raw keyword-match count for the winning mood.
    If no mood clears the threshold, returns (Mood.NEUTRAL, 0).
    """
    q = query.lower()
    scores: dict[Mood, int] = {m: 0 for m in Mood if m != Mood.NEUTRAL}

    for mood, phrases in _SIGNALS.items():
        for phrase in phrases:
            if phrase in q:
                scores[mood] += 1

    best_mood = max(scores, key=lambda m: scores[m])
    best_score = scores[best_mood]

    if best_score < _THRESHOLD:
        return Mood.NEUTRAL, 0

    return best_mood, best_score
