"""
Query intent classifier for Gita Wisdom Guide.

Detects one of four query types before any LLM or RAG work is done:

  GREETING  — salutations, how-are-you, opening pleasantries
  FACTUAL   — GK questions about the Gita / Mahabharata (no personal guidance needed)
  OFF_TOPIC — completely unrelated to wisdom / Gita / Mahabharata
  SPIRITUAL — personal challenges, life guidance, emotional struggles (default)

Design principle: scoring-based, not first-match-wins.
Each signal adds/subtracts from per-type scores; highest score wins.
Easy to extend: add new signal sets without touching existing logic.
"""

from enum import Enum
from typing import Tuple


class QueryType(str, Enum):
    GREETING = "greeting"
    FACTUAL = "factual"
    OFF_TOPIC = "off_topic"
    SPIRITUAL = "spiritual"


# ─────────────────────────────────────────────────────────────────────────────
# Signal sets
# ─────────────────────────────────────────────────────────────────────────────

_GREETING_EXACT = {
    "hi", "hello", "hey", "howdy", "yo", "sup", "hiya",
    "namaste", "namaskar", "pranam", "pranaam",
    "hare krishna", "jai shri krishna", "jai shree krishna",
    "radhe radhe", "om namah shivaya",
    "good morning", "good afternoon", "good evening", "good night",
    "how are you", "how r you", "how r u", "how are u",
    "what's up", "whats up", "what is up",
    "greetings", "salutations",
}

_GREETING_STARTS = (
    "hi ", "hello ", "hey ", "good morning", "good afternoon",
    "good evening", "good night", "namaste",
)

# Gita / Mahabharata specific terms that indicate a factual GK question
_GITA_MAHABHARATA_TERMS = {
    "gita", "bhagavad gita", "bhagavadgita", "mahabharata", "mahabharat",
    "kurukshetra", "pandava", "pandavas", "kaurava", "kauravas",
    "arjuna", "arjun", "krishna", "duryodhana", "bhishma", "drona",
    "dronacharya", "yudhishthira", "bhima", "nakula", "sahadeva",
    "draupadi", "karna", "ashwatthama", "vyasa", "sanjaya", "dhritarashtra",
    "kunti", "gandhari", "abhimanyu", "subhadra", "balarama",
    "hastinapur", "hastinapura", "indraprastha", "dwarka",
    "chapter", "verse", "shloka", "sloka", "adhyaya",
    "upanishad", "vedas", "purana", "itihasa",
}

# Question starters that signal factual intent (when combined with Gita terms)
_FACTUAL_QUESTION_STARTERS = (
    "who is", "who was", "who are", "who were",
    "what is", "what was", "what are", "what were",
    "where is", "where was", "when is", "when was", "when did",
    "how many", "how much", "how long", "how old",
    "which chapter", "which verse", "which book",
    "tell me about", "describe", "explain",
    "what happened", "what does", "what did",
    "list", "name the", "give me",
)

# Strong spiritual / personal signals
_SPIRITUAL_SIGNALS = {
    # Emotions
    "feel", "feeling", "felt", "emotion", "emotional",
    "sad", "happy", "angry", "anxious", "worried", "scared",
    "depressed", "lonely", "guilty", "ashamed", "hopeless",
    # Personal struggle words
    "struggle", "struggling", "problem", "challenge", "difficult",
    "confused", "lost", "stuck", "help me", "help with",
    "i am", "i'm", "i have", "i've", "i feel", "i need",
    "my life", "my mind", "my heart", "my family", "my job",
    "my career", "my relationship", "my marriage",
    # Purpose / meaning
    "purpose", "meaning", "direction", "path", "dharma",
    "should i", "should i do", "what should",
    # Inner states
    "peace", "calm", "anxiety", "stress", "fear", "anger",
    "forgive", "forgiveness", "attachment", "detachment",
    "desire", "ego", "karma", "duty",
}

# Signals that push strongly toward OFF_TOPIC
_OFF_TOPIC_SIGNALS = {
    # Tech
    "code", "coding", "programming", "software", "javascript",
    "python script", "algorithm", "database", "sql", "html", "css",
    "debug", "error in code", "function", "api call", "git",
    # Entertainment
    "movie", "film", "song", "music", "playlist", "netflix",
    "cricket", "football", "ipl", "match score",
    # Food / travel
    "recipe", "cook", "restaurant", "hotel", "flight", "ticket",
    # Finance
    "stock price", "share price", "bitcoin", "crypto",
    # Weather / news
    "weather", "forecast", "news today", "latest news",
    # Math / calculations
    "calculate", "what is 2", "what is 3", "solve this",
    # Misc
    "translate", "translation", "what time is it", "current time",
    "remind me", "set alarm", "send email",
}


# ─────────────────────────────────────────────────────────────────────────────
# Classifier
# ─────────────────────────────────────────────────────────────────────────────

def classify_query(query: str) -> Tuple[QueryType, float]:
    """
    Returns (QueryType, confidence_score 0.0–1.0).

    Confidence is indicative — use it for logging/debugging, not hard gates.
    """
    q = query.strip().lower().rstrip("!?.,;:")
    words = q.split()

    scores = {
        QueryType.GREETING:  0.0,
        QueryType.FACTUAL:   0.0,
        QueryType.OFF_TOPIC: 0.0,
        QueryType.SPIRITUAL: 0.1,   # default small bias toward spiritual
    }

    # ── Greeting signals ──────────────────────────────────────────────────
    if q in _GREETING_EXACT:
        scores[QueryType.GREETING] += 3.0

    if any(q.startswith(s) for s in _GREETING_STARTS):
        scores[QueryType.GREETING] += 2.0

    # Very short (≤3 words) with no Gita/spiritual terms → likely greeting
    if len(words) <= 3 and not _GITA_MAHABHARATA_TERMS.intersection(words):
        if not _SPIRITUAL_SIGNALS.intersection(words):
            scores[QueryType.GREETING] += 1.0

    # ── Off-topic signals ─────────────────────────────────────────────────
    for signal in _OFF_TOPIC_SIGNALS:
        if signal in q:
            scores[QueryType.OFF_TOPIC] += 2.0
            break   # one strong off-topic hit is enough

    # ── Factual signals ───────────────────────────────────────────────────
    has_gita_term = bool(_GITA_MAHABHARATA_TERMS.intersection(set(words)))
    has_factual_starter = any(q.startswith(s) or s in q for s in _FACTUAL_QUESTION_STARTERS)

    if has_gita_term:
        scores[QueryType.FACTUAL] += 1.5
    if has_factual_starter:
        scores[QueryType.FACTUAL] += 1.0
    if has_gita_term and has_factual_starter:
        scores[QueryType.FACTUAL] += 1.0  # combined bonus

    # ── Spiritual signals ─────────────────────────────────────────────────
    spiritual_hits = sum(1 for s in _SPIRITUAL_SIGNALS if s in q)
    scores[QueryType.SPIRITUAL] += spiritual_hits * 0.5

    # Personal pronouns are a strong spiritual indicator
    if any(p in words for p in ("i", "me", "my", "myself", "i'm", "i've", "i'll")):
        scores[QueryType.SPIRITUAL] += 1.0

    # Long, sentence-like queries are almost always spiritual
    if len(words) > 10:
        scores[QueryType.SPIRITUAL] += 0.5

    # ── Resolve ───────────────────────────────────────────────────────────
    winner = max(scores, key=lambda t: scores[t])

    # Normalize confidence to [0, 1] using softmax-like ratio
    total = sum(scores.values()) or 1.0
    confidence = round(scores[winner] / total, 2)

    return winner, confidence
