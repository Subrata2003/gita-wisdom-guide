from fastapi import APIRouter, HTTPException, Request

from backend.models.schemas import QueryRequest, WisdomResponse, VerseInfo, SessionHistoryResponse
from backend.core.session_manager import SessionManager
from backend.core.query_classifier import classify_query, QueryType
from backend.core.prompts import get_off_topic_response

router = APIRouter()

_session_manager = SessionManager(max_history=10, session_ttl_hours=2)


@router.post("/query", response_model=WisdomResponse)
async def get_wisdom(request: Request, body: QueryRequest):
    retriever = getattr(request.app.state, "retriever", None)
    llm_handler = getattr(request.app.state, "llm_handler", None)

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
