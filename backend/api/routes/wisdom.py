import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.models.schemas import QueryRequest, WisdomResponse, VerseInfo, SessionHistoryResponse
from backend.core.session_manager import SessionManager
from backend.core.query_classifier import classify_query, QueryType
from backend.core.prompts import get_off_topic_response, MENTAL_HEALTH_KEYWORDS, MENTAL_HEALTH_DISCLAIMER
from backend.core.mood_detector import detect_mood

router = APIRouter()

_session_manager = SessionManager(max_history=10, session_ttl_hours=2)


@router.post("/query", response_model=WisdomResponse)
async def get_wisdom(request: Request, body: QueryRequest):
    retriever      = getattr(request.app.state, "retriever",   None)
    llm_handler    = getattr(request.app.state, "llm_handler", None)
    sanskrit_index = getattr(request.app.state, "sanskrit",    {})

    if not retriever or not llm_handler:
        raise HTTPException(
            status_code=503,
            detail="Service is still initializing. Please wait a moment and try again.",
        )

    # ── Validate / create session ─────────────────────────────────────────────
    session_id = body.session_id
    if not session_id or not _session_manager.get_session(session_id):
        session_id = _session_manager.create_session()

    # ── Classify intent ───────────────────────────────────────────────────────
    query_type, _confidence = classify_query(body.query)

    # ── OFF_TOPIC: static redirect, no LLM, no RAG ───────────────────────────
    if query_type == QueryType.OFF_TOPIC:
        return WisdomResponse(
            response=get_off_topic_response(),
            used_verses=[],
            themes=[],
            session_id=session_id,
            error=False,
        )

    # ── GREETING / FACTUAL: LLM only, no RAG ─────────────────────────────────
    if query_type in (QueryType.GREETING, QueryType.FACTUAL):
        result = llm_handler.generate_typed_response(body.query, query_type)

        _session_manager.add_to_history(
            session_id, body.query, result["response"], [], result.get("themes", [])
        )

        return WisdomResponse(
            response=result["response"],
            used_verses=[],
            themes=[],
            session_id=session_id,
            error=result.get("error", False),
        )

    # ── SPIRITUAL: full RAG + deep guidance ──────────────────────────────────
    conversation_context = _session_manager.get_conversation_context(session_id, last_n=3)

    context = retriever.create_context_for_llm(
        body.query,
        conversation_context=conversation_context,
        max_context_length=3500,
    )

    result = llm_handler.generate_response(body.query, context)

    _session_manager.add_to_history(
        session_id,
        body.query,
        result["response"],
        result.get("used_verses", []),
        result.get("themes", []),
    )

    verses = [
        VerseInfo(
            chapter=v.get("chapter", 0),
            verse=v.get("verse", 0),
            text=v.get("text", ""),
            theme=v.get("theme", "general"),
            verse_id=v.get("verse_id", ""),
            relevance_score=v.get("relevance_score", 0.0),
            sanskrit=sanskrit_index.get(
                f"{v.get('chapter', 0)}_{v.get('verse', 0)}", {}
            ).get("sanskrit"),
            transliteration=sanskrit_index.get(
                f"{v.get('chapter', 0)}_{v.get('verse', 0)}", {}
            ).get("transliteration"),
        )
        for v in result.get("used_verses", [])
    ]

    return WisdomResponse(
        response=result["response"],
        used_verses=verses,
        themes=result.get("themes", []),
        session_id=session_id,
        error=result.get("error", False),
    )


_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",     # tells Nginx not to buffer SSE
    "Connection": "keep-alive",
}

def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/query/stream")
async def stream_wisdom(request: Request, body: QueryRequest):
    """
    Streaming version of /query using Server-Sent Events.
    Events:
      {"type": "token",  "content": "<text chunk>"}
      {"type": "done",   "verses": [...], "themes": [...], "session_id": "..."}
      {"type": "error",  "message": "<reason>"}
    """
    retriever      = getattr(request.app.state, "retriever",   None)
    llm_handler    = getattr(request.app.state, "llm_handler", None)
    sanskrit_index = getattr(request.app.state, "sanskrit",    {})

    if not retriever or not llm_handler:
        def _err():
            yield _sse({"type": "error", "message": "Service is still initializing. Please wait."})
        return StreamingResponse(_err(), media_type="text/event-stream", headers=_SSE_HEADERS)

    session_id = body.session_id
    if not session_id or not _session_manager.get_session(session_id):
        session_id = _session_manager.create_session()

    query_type, _ = classify_query(body.query)

    # ── OFF_TOPIC: static, no LLM ────────────────────────────────────────────
    if query_type == QueryType.OFF_TOPIC:
        text = get_off_topic_response()
        def _off_topic():
            yield _sse({"type": "token",  "content": text})
            yield _sse({"type": "done",   "verses": [], "themes": [], "session_id": session_id})
        return StreamingResponse(_off_topic(), media_type="text/event-stream", headers=_SSE_HEADERS)

    # ── GREETING / FACTUAL: async stream without RAG ─────────────────────────
    if query_type in (QueryType.GREETING, QueryType.FACTUAL):
        async def _typed():
            full = ""
            async for chunk in llm_handler.stream_typed_response_async(body.query, query_type):
                full += chunk
                yield _sse({"type": "token", "content": chunk})
            _session_manager.add_to_history(session_id, body.query, full, [], [])
            yield _sse({"type": "done", "verses": [], "themes": [], "session_id": session_id})
        return StreamingResponse(_typed(), media_type="text/event-stream", headers=_SSE_HEADERS)

    # ── SPIRITUAL: RAG retrieval first, then async stream ────────────────────
    conversation_context = _session_manager.get_conversation_context(session_id, last_n=3)
    context = retriever.create_context_for_llm(
        body.query,
        conversation_context=conversation_context,
        max_context_length=3500,
    )
    needs_disclaimer = any(kw in body.query.lower() for kw in MENTAL_HEALTH_KEYWORDS)

    # Detect seeker's emotional state — injects tone overlay into system prompt
    mood, _mood_score = detect_mood(body.query)
    context["mood"] = mood.value

    def _enrich(v):
        key = f"{v.get('chapter', 0)}_{v.get('verse', 0)}"
        sk  = sanskrit_index.get(key, {})
        return {
            "chapter":         v.get("chapter", 0),
            "verse":           v.get("verse", 0),
            "text":            v.get("text", ""),
            "theme":           v.get("theme", "general"),
            "verse_id":        v.get("verse_id", ""),
            "relevance_score": v.get("relevance_score", 0.0),
            "sanskrit":        sk.get("sanskrit"),
            "transliteration": sk.get("transliteration"),
        }

    async def _spiritual():
        full = ""
        async for chunk in llm_handler.stream_response_async(body.query, context):
            full += chunk
            yield _sse({"type": "token", "content": chunk})

        if needs_disclaimer:
            full += MENTAL_HEALTH_DISCLAIMER
            yield _sse({"type": "token", "content": MENTAL_HEALTH_DISCLAIMER})

        used_verses = context.get("used_verses", [])
        themes      = context.get("query_themes", [])
        _session_manager.add_to_history(session_id, body.query, full, used_verses, themes)

        verses_payload = [_enrich(v) for v in used_verses]
        yield _sse({"type": "done", "verses": verses_payload, "themes": themes, "session_id": session_id, "mood": mood.value})

    return StreamingResponse(_spiritual(), media_type="text/event-stream", headers=_SSE_HEADERS)


@router.get("/session/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    history = _session_manager.get_history(session_id)
    return SessionHistoryResponse(session_id=session_id, history=history)


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    _session_manager.delete_session(session_id)
    return {"message": "Session cleared", "session_id": session_id}


@router.get("/sessions/stats")
async def session_stats():
    return _session_manager.get_stats()
