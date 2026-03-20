"""
Enhanced RAG Retrieval Engine for Gita Wisdom Guide.

Key improvements over the original:
1. Multi-theme extraction (not first-match-wins)
2. Query expansion with spiritual synonyms
3. Correct relevance score formula for L2 distance with normalized vectors
4. Score threshold filtering (removes irrelevant results)
5. Content-based deduplication (not just verse_id)
6. Larger context window (3500 chars)
7. Conversation context injection support
8. Separate verse/chunk handling for cleaner LLM context
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

_ROOT = Path(__file__).parent.parent.parent
for _p in [str(_ROOT), str(_ROOT / "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from vector_store import GitaVectorStore  # noqa: E402


# ─────────────────────────────────────────────────────────────
# Topic → Theme mapping (expanded from original)
# ─────────────────────────────────────────────────────────────
TOPIC_THEMES: Dict[str, List[str]] = {
    "stress": ["peace", "meditation", "detachment", "action"],
    "depression": ["peace", "knowledge", "soul", "devotion"],
    "anxiety": ["peace", "meditation", "detachment"],
    "fear": ["peace", "knowledge", "soul", "duty"],
    "anger": ["peace", "detachment", "duty", "knowledge"],
    "rage": ["peace", "detachment", "duty"],
    "confusion": ["knowledge", "duty", "action", "soul"],
    "lost": ["knowledge", "duty", "soul", "peace"],
    "purpose": ["duty", "action", "devotion", "knowledge"],
    "dharma": ["duty", "action", "devotion"],
    "meaning": ["duty", "soul", "knowledge", "devotion"],
    "death": ["soul", "knowledge", "detachment"],
    "dying": ["soul", "knowledge", "detachment"],
    "grief": ["soul", "knowledge", "detachment", "peace"],
    "sorrow": ["peace", "detachment", "soul", "knowledge"],
    "suffering": ["peace", "detachment", "knowledge", "duty"],
    "relationships": ["detachment", "devotion", "duty", "peace"],
    "love": ["devotion", "soul", "peace"],
    "family": ["duty", "detachment", "devotion"],
    "work": ["action", "duty", "detachment", "peace"],
    "career": ["action", "duty", "detachment"],
    "job": ["action", "duty", "detachment"],
    "success": ["action", "detachment", "duty"],
    "failure": ["peace", "detachment", "action", "knowledge"],
    "defeat": ["peace", "detachment", "knowledge"],
    "ego": ["detachment", "knowledge", "soul"],
    "pride": ["detachment", "knowledge"],
    "desire": ["detachment", "knowledge", "action"],
    "attachment": ["detachment", "knowledge", "soul"],
    "jealousy": ["detachment", "duty", "peace"],
    "envy": ["detachment", "duty", "peace"],
    "loneliness": ["devotion", "soul", "meditation"],
    "alone": ["devotion", "soul", "meditation"],
    "god": ["devotion", "knowledge", "soul"],
    "divine": ["devotion", "knowledge", "soul"],
    "prayer": ["devotion", "meditation", "soul"],
    "meditation": ["meditation", "peace", "soul"],
    "yoga": ["meditation", "action", "knowledge"],
    "mind": ["meditation", "peace", "knowledge"],
    "money": ["detachment", "action", "duty"],
    "wealth": ["detachment", "action", "duty"],
    "forgiveness": ["peace", "detachment", "knowledge"],
    "justice": ["duty", "knowledge", "action"],
    "war": ["duty", "action", "knowledge"],
    "fight": ["duty", "action", "knowledge"],
    "health": ["soul", "action", "meditation"],
    "body": ["soul", "knowledge", "detachment"],
    "truth": ["knowledge", "duty", "soul"],
    "happiness": ["peace", "detachment", "soul"],
    "joy": ["peace", "devotion", "soul"],
}

# ─────────────────────────────────────────────────────────────
# Query expansion (adds spiritual context terms)
# ─────────────────────────────────────────────────────────────
QUERY_EXPANSIONS: Dict[str, str] = {
    "stress": "stress burden restless troubled disturbed overwhelm",
    "depression": "depression sadness sorrow grief despair melancholy",
    "anxiety": "anxiety worry apprehension restless uncertain dread",
    "fear": "fear dread apprehension worried anxious uncertain",
    "anger": "anger rage wrath frustration irritation hostile",
    "confusion": "confused uncertain lost unclear direction bewildered",
    "purpose": "purpose meaning dharma duty direction goal path",
    "failure": "failure defeat loss unsuccessful fallen stumbled",
    "success": "success achievement victory accomplish result fruit",
    "work": "work duty action karma profession karma yoga",
    "relationships": "relationships love family friends attachment bond",
    "god": "god divine Krishna supreme consciousness Brahman",
    "death": "death dying immortal eternal soul rebirth",
    "peace": "peace calm tranquil serene harmony equanimity",
    "meditation": "meditation yoga concentration mind awareness samadhi",
    "grief": "grief sorrow loss mourning lamentation",
    "ego": "ego pride self-importance ahamkara arrogance",
    "desire": "desire craving attachment want longing",
    "forgiveness": "forgiveness letting go acceptance compassion",
    "happiness": "happiness bliss joy contentment ananda",
}


class EnhancedGitaRetriever:
    """
    Multi-strategy retrieval with:
    - Query expansion
    - Weighted multi-theme search
    - Correct distance-to-similarity conversion
    - Score threshold filtering
    - Smart deduplication
    """

    def __init__(self, vector_store: GitaVectorStore, relevance_threshold: float = 0.20):
        self.vector_store = vector_store
        self.relevance_threshold = relevance_threshold

    # ─── Query preprocessing ────────────────────────────────

    def preprocess_query(self, query: str) -> Tuple[str, str]:
        """
        Returns (original_query, expanded_query).
        Keeps original case for display; expands lowercase for retrieval.
        """
        expanded = query.lower().strip()

        # Expand contractions
        contractions = {
            "i'm": "i am",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "i've": "i have",
            "i'll": "i will",
            "i'd": "i would",
            "it's": "it is",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "didn't": "did not",
            "couldn't": "could not",
            "shouldn't": "should not",
        }
        for abbrev, full in contractions.items():
            expanded = expanded.replace(abbrev, full)

        # Append expansion terms (don't replace, just augment)
        expansion_parts = []
        for keyword, expansion in QUERY_EXPANSIONS.items():
            if keyword in expanded:
                expansion_parts.append(expansion)

        if expansion_parts:
            expanded = expanded + " " + " ".join(expansion_parts)

        return query, expanded

    # ─── Theme extraction ───────────────────────────────────

    def extract_query_themes(self, query: str) -> List[str]:
        """
        Extract ALL relevant themes (not first-match-wins).
        Returns themes sorted by how many topics point to them.
        """
        query_lower = query.lower()
        theme_scores: Dict[str, int] = {}

        for topic, themes in TOPIC_THEMES.items():
            if topic in query_lower:
                for rank, theme in enumerate(themes):
                    # Earlier themes in the list get higher weight
                    theme_scores[theme] = theme_scores.get(theme, 0) + (len(themes) - rank)

        if not theme_scores:
            return ["general"]

        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, _ in sorted_themes[:4]]

    # ─── Core retrieval ─────────────────────────────────────

    def retrieve_relevant_verses(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Multi-strategy retrieval:
        1. Theme-filtered semantic search (top 3 themes)
        2. General semantic search with expanded query
        3. General semantic search with original query
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

        # 3. Fallback: search with original query (catches cases where expansion hurts recall)
        if original_query.lower() != expanded_query:
            try:
                raw = self.vector_store.search_similar(original_query, n_results=5)
                all_results.extend(self._format_results(raw))
            except Exception:
                pass

        # Filter by relevance threshold
        filtered = [r for r in all_results if r["relevance_score"] >= self.relevance_threshold]

        # If filtering left us with nothing, relax threshold slightly
        if not filtered:
            filtered = sorted(all_results, key=lambda x: x["relevance_score"], reverse=True)[:5]

        # Deduplicate
        unique = self._smart_deduplicate(filtered)

        # Sort by score (descending)
        unique.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Prefer individual verses; pad with chunks if needed
        verses = [r for r in unique if r["content_type"] == "verse"]
        chunks = [r for r in unique if r["content_type"] == "chunk"]
        combined = verses[:max_results]
        if len(combined) < max(4, max_results // 2):
            combined += chunks[: max_results - len(combined)]

        return combined[:max_results]

    # ─── Formatting & deduplication ─────────────────────────

    def _format_results(self, raw: Dict) -> List[Dict]:
        """
        Convert ChromaDB results to structured dicts.

        Distance conversion (robust for both L2 and cosine):
        - ChromaDB default = L2.  For unit-norm vectors (all-MiniLM-L6-v2):
          L2² = 2*(1 - cos_sim)  →  cos_sim = 1 - L2²/2
          L2 ∈ [0, √2 ≈ 1.41] for non-negative cos_sim
        - If cosine metric was specified: distance ∈ [0, 2], relevance = 1 - distance/2
        We use the safe formula: relevance = max(0, 1 - distance²/2) which works for L2
        and also gives reasonable values for cosine distance.
        """
        formatted = []
        if not raw.get("documents") or not raw["documents"][0]:
            return formatted

        for doc, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            # Robust distance → similarity conversion
            # For L2 with normalized vectors: relevance = 1 - dist²/2
            # For cosine distance [0,2]: relevance = 1 - dist/2
            # We detect which by checking if dist > sqrt(2) ≈ 1.41 (implies cosine)
            if dist > 1.5:
                relevance_score = max(0.0, 1.0 - dist / 2.0)
            else:
                relevance_score = max(0.0, 1.0 - (dist ** 2) / 2.0)

            chapter_str = meta.get("chapter", "0")
            verse_str = meta.get("verse", "0")

            formatted.append(
                {
                    "text": doc,
                    "chapter": int(chapter_str) if chapter_str.isdigit() else 0,
                    "verse": int(verse_str) if verse_str.isdigit() else 0,
                    "verse_id": meta.get("verse_id", ""),
                    "theme": meta.get("theme", "general"),
                    "content_type": meta.get("content_type", "verse"),
                    "relevance_score": round(relevance_score, 3),
                    "distance": round(dist, 4),
                }
            )

        return formatted

    def _smart_deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Deduplicate by verse_id AND text prefix (catches chunks overlapping same verses)."""
        seen_verse_ids: set = set()
        seen_text_prefixes: set = set()
        unique = []

        for r in results:
            vid = r.get("verse_id", "")
            prefix = r["text"][:80] if r.get("text") else ""

            if vid and vid in seen_verse_ids:
                continue
            if prefix and prefix in seen_text_prefixes:
                continue

            if vid:
                seen_verse_ids.add(vid)
            if prefix:
                seen_text_prefixes.add(prefix)

            unique.append(r)

        return unique

    # ─── LLM context builder ────────────────────────────────

    def create_context_for_llm(
        self,
        query: str,
        conversation_context: str = "",
        max_context_length: int = 3500,
    ) -> Dict:
        """
        Build the full context dict that the LLM handler needs:
        - formatted_context: verse texts formatted for the prompt
        - used_verses: structured list for the API response
        - query_themes: detected themes
        - conversation_context: prior Q&A for continuity
        """
        relevant_verses = self.retrieve_relevant_verses(query)
        themes = self.extract_query_themes(query)

        context_parts = []
        used_verses = []
        total_length = 0

        # Add individual verses first (more precise for LLM)
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
