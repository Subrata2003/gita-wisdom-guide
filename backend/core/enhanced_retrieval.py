"""
Enhanced RAG Retrieval Engine for Gita Wisdom Guide.

Key design points:
1. Topic→theme mapping and query expansions loaded from themes_config.json
   (edit that file to tune without touching code)
2. Multi-theme extraction — not first-match-wins
3. Query expansion with spiritual synonyms
4. Correct relevance score formula for L2 distance with normalized vectors
5. Score threshold filtering
6. Content-based deduplication
7. Conversation context injection support
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

_ROOT = Path(__file__).parent.parent.parent
for _p in [str(_ROOT), str(_ROOT / "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from vector_store import GitaVectorStore  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# Load theme config from JSON (with hardcoded fallback)
# ─────────────────────────────────────────────────────────────────────────────

_CONFIG_PATH = Path(__file__).parent.parent / "data" / "themes_config.json"

_FALLBACK_TOPIC_THEMES: Dict[str, List[str]] = {
    "stress": ["peace", "meditation", "detachment", "action"],
    "depression": ["peace", "knowledge", "soul", "devotion"],
    "anxiety": ["peace", "meditation", "detachment"],
    "fear": ["peace", "knowledge", "soul", "duty"],
    "anger": ["peace", "detachment", "duty", "knowledge"],
    "confusion": ["knowledge", "duty", "action", "soul"],
    "lost": ["knowledge", "duty", "soul", "peace"],
    "purpose": ["duty", "action", "devotion", "knowledge"],
    "grief": ["soul", "knowledge", "detachment", "peace"],
    "failure": ["peace", "detachment", "action", "knowledge"],
    "work": ["action", "duty", "detachment", "peace"],
    "ego": ["detachment", "knowledge", "soul"],
    "desire": ["detachment", "knowledge", "action"],
    "death": ["soul", "knowledge", "detachment"],
    "peace": ["peace", "meditation", "soul"],
    "happiness": ["peace", "detachment", "soul"],
}

_FALLBACK_QUERY_EXPANSIONS: Dict[str, str] = {
    "stress": "stress burden restless troubled disturbed overwhelm",
    "depression": "depression sadness sorrow grief despair melancholy",
    "anxiety": "anxiety worry apprehension restless uncertain dread",
    "fear": "fear dread apprehension worried anxious uncertain",
    "purpose": "purpose meaning dharma duty direction goal path",
    "failure": "failure defeat loss unsuccessful fallen stumbled",
    "peace": "peace calm tranquil serene harmony equanimity",
    "grief": "grief sorrow loss mourning lamentation",
}


def _load_theme_config() -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        topic_themes = cfg.get("topic_themes", _FALLBACK_TOPIC_THEMES)
        query_expansions = cfg.get("query_expansions", _FALLBACK_QUERY_EXPANSIONS)
        return topic_themes, query_expansions
    except Exception as e:
        print(f"WARNING: Could not load themes_config.json ({e}). Using defaults.")
        return _FALLBACK_TOPIC_THEMES, _FALLBACK_QUERY_EXPANSIONS


TOPIC_THEMES, QUERY_EXPANSIONS = _load_theme_config()


class EnhancedGitaRetriever:
    """
    Multi-strategy retrieval:
    - Query expansion from themes_config.json
    - Weighted multi-theme search
    - L2 distance → similarity conversion
    - Score threshold filtering
    - Smart deduplication
    """

    def __init__(self, vector_store: GitaVectorStore, relevance_threshold: float = 0.20):
        self.vector_store = vector_store
        self.relevance_threshold = relevance_threshold

    # ─── Query preprocessing ──────────────────────────────────────────────────

    def preprocess_query(self, query: str) -> Tuple[str, str]:
        """Returns (original_query, expanded_query)."""
        expanded = query.lower().strip()

        contractions = {
            "i'm": "i am", "can't": "cannot", "won't": "will not",
            "don't": "do not", "i've": "i have", "i'll": "i will",
            "i'd": "i would", "it's": "it is", "isn't": "is not",
            "aren't": "are not", "wasn't": "was not", "didn't": "did not",
            "couldn't": "could not", "shouldn't": "should not",
        }
        for abbrev, full in contractions.items():
            expanded = expanded.replace(abbrev, full)

        expansion_parts = [
            exp for kw, exp in QUERY_EXPANSIONS.items() if kw in expanded
        ]
        if expansion_parts:
            expanded = expanded + " " + " ".join(expansion_parts)

        return query, expanded

    # ─── Theme extraction ─────────────────────────────────────────────────────

    def extract_query_themes(self, query: str) -> List[str]:
        """
        Extract ALL relevant themes (not first-match-wins).
        Returns themes sorted by cumulative relevance weight.
        """
        query_lower = query.lower()
        theme_scores: Dict[str, int] = {}

        for topic, themes in TOPIC_THEMES.items():
            if topic in query_lower:
                for rank, theme in enumerate(themes):
                    theme_scores[theme] = theme_scores.get(theme, 0) + (len(themes) - rank)

        if not theme_scores:
            return ["general"]

        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, _ in sorted_themes[:4]]

    # ─── Core retrieval ───────────────────────────────────────────────────────

    def retrieve_relevant_verses(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Multi-strategy retrieval:
        1. Theme-filtered semantic search (top 3 themes)
        2. General semantic search with expanded query
        3. General semantic search with original query (catches expansion over-recall)

        Then: threshold filter → deduplicate → sort → return top N
        """
        original_query, expanded_query = self.preprocess_query(query)
        themes = self.extract_query_themes(original_query)

        all_results: List[Dict] = []

        # 1. Theme-filtered searches
        for theme in themes[:3]:
            if theme == "general":
                continue
            try:
                raw = self.vector_store.search_by_theme(expanded_query, theme, n_results=4)
                all_results.extend(self._format_results(raw))
            except Exception:
                pass

        # 2. General semantic search with expanded query
        try:
            raw = self.vector_store.search_similar(expanded_query, n_results=8)
            all_results.extend(self._format_results(raw))
        except Exception:
            pass

        # 3. Fallback with original query
        if original_query.lower() != expanded_query:
            try:
                raw = self.vector_store.search_similar(original_query, n_results=5)
                all_results.extend(self._format_results(raw))
            except Exception:
                pass

        # Filter by relevance threshold
        filtered = [r for r in all_results if r["relevance_score"] >= self.relevance_threshold]

        # Relax threshold if nothing survived
        if not filtered:
            filtered = sorted(all_results, key=lambda x: x["relevance_score"], reverse=True)[:5]

        unique = self._smart_deduplicate(filtered)
        unique.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Prefer full verses; pad with chunks if needed
        verses = [r for r in unique if r["content_type"] == "verse"]
        chunks = [r for r in unique if r["content_type"] == "chunk"]
        combined = verses[:max_results]
        if len(combined) < max(4, max_results // 2):
            combined += chunks[: max_results - len(combined)]

        return combined[:max_results]

    # ─── Formatting ───────────────────────────────────────────────────────────

    def _format_results(self, raw: Dict) -> List[Dict]:
        """
        Convert ChromaDB results to structured dicts.

        Distance → similarity:
        - L2 with unit-norm vectors: relevance = 1 - dist²/2
        - Cosine distance [0,2]:     relevance = 1 - dist/2
        We detect which by checking dist > 1.5 (only possible with cosine).
        """
        formatted = []
        if not raw.get("documents") or not raw["documents"][0]:
            return formatted

        for doc, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            if dist > 1.5:
                relevance_score = max(0.0, 1.0 - dist / 2.0)
            else:
                relevance_score = max(0.0, 1.0 - (dist ** 2) / 2.0)

            chapter_str = meta.get("chapter", "0")
            verse_str = meta.get("verse", "0")

            formatted.append({
                "text": doc,
                "chapter": int(chapter_str) if str(chapter_str).isdigit() else 0,
                "verse": int(verse_str) if str(verse_str).isdigit() else 0,
                "verse_id": meta.get("verse_id", ""),
                "theme": meta.get("theme", "general"),
                "content_type": meta.get("content_type", "verse"),
                "relevance_score": round(relevance_score, 3),
                "distance": round(dist, 4),
            })

        return formatted

    def _smart_deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Deduplicate by verse_id AND text prefix."""
        seen_ids: set = set()
        seen_prefixes: set = set()
        unique = []

        for r in results:
            vid = r.get("verse_id", "")
            prefix = r["text"][:80] if r.get("text") else ""

            if vid and vid in seen_ids:
                continue
            if prefix and prefix in seen_prefixes:
                continue

            if vid:
                seen_ids.add(vid)
            if prefix:
                seen_prefixes.add(prefix)

            unique.append(r)

        return unique

    # ─── LLM context builder ─────────────────────────────────────────────────

    def create_context_for_llm(
        self,
        query: str,
        conversation_context: str = "",
        max_context_length: int = 3500,
    ) -> Dict:
        """
        Build the full context dict that the LLM handler needs:
        - formatted_context  : verse texts formatted for the prompt
        - used_verses        : structured list for the API response
        - query_themes       : detected themes
        - conversation_context: prior Q&A for continuity
        """
        relevant_verses = self.retrieve_relevant_verses(query)
        themes = self.extract_query_themes(query)

        context_parts = []
        used_verses = []
        total_length = 0

        # Full verses first
        for v in relevant_verses:
            if v["content_type"] != "verse":
                continue
            label = f"[Chapter {v['chapter']}, Verse {v['verse']} | Theme: {v['theme'].title()}]"
            verse_text = f"{label}\n{v['text']}"

            if total_length + len(verse_text) <= max_context_length:
                context_parts.append(verse_text)
                used_verses.append(v)
                total_length += len(verse_text)
            else:
                break

        # Pad with chunk context if still under 60% capacity
        if total_length < max_context_length * 0.6:
            for v in relevant_verses:
                if v["content_type"] != "chunk":
                    continue
                chunk_text = f"[Related context]\n{v['text'][:350]}"
                if total_length + len(chunk_text) <= max_context_length:
                    context_parts.append(chunk_text)
                    total_length += len(chunk_text)

        return {
            "formatted_context": "\n\n".join(context_parts),
            "used_verses": used_verses,
            "query_themes": themes,
            "total_verses": len(used_verses),
            "conversation_context": conversation_context,
        }
