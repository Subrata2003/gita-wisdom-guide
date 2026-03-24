import datetime

from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional

router = APIRouter()

VALID_THEMES = [
    "duty",
    "detachment",
    "knowledge",
    "devotion",
    "action",
    "soul",
    "peace",
    "meditation",
    "general",
]

THEME_QUERIES = {
    "duty":        "righteous duty dharma obligation responsibility",
    "detachment":  "detachment non-attachment renunciation surrender",
    "knowledge":   "wisdom knowledge self-realization truth understanding",
    "devotion":    "devotion love worship bhakti dedication",
    "action":      "action karma work performance activity",
    "soul":        "soul atman eternal self consciousness",
    "peace":       "peace tranquility calm serenity equanimity",
    "meditation":  "meditation yoga concentration mind stillness",
    "general":     "wisdom teaching guidance",
}


@router.get("/themes")
async def get_themes():
    """Return all available spiritual themes."""
    theme_info = {
        "duty":        {"emoji": "⚖️",  "description": "Dharma, righteous action, obligations"},
        "detachment":  {"emoji": "🌊",  "description": "Non-attachment, renunciation, surrender"},
        "knowledge":   {"emoji": "📚",  "description": "Wisdom, understanding, self-realization"},
        "devotion":    {"emoji": "❤️",  "description": "Bhakti, love, worship, dedication"},
        "action":      {"emoji": "⚡",  "description": "Karma yoga, work, performance, activity"},
        "soul":        {"emoji": "✨",  "description": "Atman, the eternal self, consciousness"},
        "peace":       {"emoji": "🕊️", "description": "Tranquility, calm, serenity, equanimity"},
        "meditation":  {"emoji": "🧘",  "description": "Yoga, concentration, mindfulness"},
        "general":     {"emoji": "🕉️", "description": "General Gita wisdom"},
    }
    return {"themes": theme_info}


@router.get("/verses/search")
async def search_verses(
    request: Request,
    q: Optional[str] = Query(None, description="Free-text semantic search query"),
    theme: Optional[str] = Query(None, description="Filter by spiritual theme"),
    chapter: Optional[int] = Query(None, ge=1, le=18, description="Filter by chapter (1-18)"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
):
    """Search Gita verses by query, theme, or chapter."""
    vector_store = getattr(request.app.state, "vector_store", None)

    if not vector_store:
        raise HTTPException(status_code=503, detail="Service is still initializing")

    if theme and theme not in VALID_THEMES:
        raise HTTPException(status_code=400, detail=f"Invalid theme. Valid themes: {VALID_THEMES}")

    if q:
        results = vector_store.search_similar(q, n_results=limit)
    elif theme:
        query_text = THEME_QUERIES.get(theme, theme)
        results = vector_store.search_by_theme(query_text, theme, n_results=limit)
    elif chapter:
        results = vector_store.search_by_chapter(
            f"Chapter {chapter} teachings wisdom", chapter, n_results=limit
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: q (query), theme, or chapter",
        )

    verses = []
    if results and results.get("documents") and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            relevance = max(0.0, 1.0 - dist / 2.0) if dist > 1.5 else max(0.0, 1.0 - (dist**2) / 2.0)
            chapter_val = str(meta.get("chapter", ""))
            verse_val = str(meta.get("verse", ""))
            verses.append(
                {
                    "text": doc,
                    "chapter": int(chapter_val) if chapter_val.isdigit() else 0,
                    "verse": int(verse_val) if verse_val.isdigit() else 0,
                    "verse_id": meta.get("verse_id", ""),
                    "theme": meta.get("theme", "general"),
                    "content_type": meta.get("content_type", "verse"),
                    "relevance_score": round(relevance, 3),
                }
            )

    return {"verses": verses, "total": len(verses)}


@router.get("/verse/daily")
async def get_daily_verse(request: Request):
    """
    Returns today's verse — deterministic, changes daily.
    Same verse for every user on the same calendar day.
    """
    all_verses    = getattr(request.app.state, "all_verses",  [])
    sanskrit_index = getattr(request.app.state, "sanskrit",   {})

    if not all_verses:
        raise HTTPException(status_code=503, detail="Verse pool not loaded yet")

    # Day-of-year (1-365/366) drives the rotation — same verse all day, every day
    day_of_year = datetime.date.today().timetuple().tm_yday
    verse       = all_verses[(day_of_year - 1) % len(all_verses)]

    ch  = verse.get("chapter", 0)
    vs  = verse.get("verse",   0)
    key = f"{ch}_{vs}"
    sk  = sanskrit_index.get(key, {})

    return {
        "chapter":         ch,
        "verse":           vs,
        "verse_id":        verse.get("verse_id", ""),
        "text":            verse.get("text", ""),
        "theme":           verse.get("theme", "general"),
        "sanskrit":        sk.get("sanskrit"),
        "transliteration": sk.get("transliteration"),
        "date":            str(datetime.date.today()),
    }
