"""
Gita Wisdom Guide — FastAPI Backend v2
Run with: uvicorn backend.main:app --reload --port 8000
(from the project root: gita-wisdom-guide/)
"""

import json
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Path setup (must happen before any local imports) ─────────
ROOT_DIR = Path(__file__).parent.parent
for _p in [str(ROOT_DIR), str(ROOT_DIR / "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize heavyweight components once at startup, store on app.state."""
    print("=" * 55)
    print("  Gita Wisdom Guide API v2.0  — Starting up")
    print("=" * 55)

    # Import here (after sys.path is configured)
    from backend.config import settings
    from vector_store import GitaVectorStore
    from backend.core.enhanced_retrieval import EnhancedGitaRetriever
    from backend.core.llm_handler import EnhancedGitaLLMHandler

    print(f"Vector DB path : {settings.VECTOR_DB_PATH}")
    print(f"LLM model      : {settings.DEFAULT_LLM}")

    print("Loading vector store...")
    app.state.vector_store = GitaVectorStore(
        collection_name=settings.COLLECTION_NAME,
        persist_directory=settings.VECTOR_DB_PATH,
    )

    print("Initializing enhanced retriever...")
    app.state.retriever = EnhancedGitaRetriever(
        app.state.vector_store,
        relevance_threshold=settings.RELEVANCE_THRESHOLD,
    )

    print("Initializing LLM handler...")
    app.state.llm_handler = EnhancedGitaLLMHandler()

    # Sanskrit lookup — loaded once, served from memory (tiny ~500 KB)
    sanskrit_path = ROOT_DIR / "data" / "sanskrit_lookup.json"
    if sanskrit_path.exists():
        with open(sanskrit_path, encoding="utf-8") as _f:
            app.state.sanskrit = json.load(_f)
        print(f"Sanskrit index : {len(app.state.sanskrit)} verses loaded")
    else:
        app.state.sanskrit = {}
        print("Sanskrit index : not found — run  python data/fetch_sanskrit.py  once")

    # All individual verses — used for Daily Verse feature
    gita_data_path = ROOT_DIR / "data" / "processed_gita_data.json"
    if gita_data_path.exists():
        with open(gita_data_path, encoding="utf-8") as _f:
            _all_docs = json.load(_f)
        app.state.all_verses = [
            d for d in _all_docs
            if d.get("content_type") == "verse"
            and d.get("chapter") and d.get("verse")
        ]
        print(f"Verse pool     : {len(app.state.all_verses)} verses for daily feature")
    else:
        app.state.all_verses = []

    info = app.state.vector_store.get_collection_info()
    print(f"Vector store   : {info.get('document_count', 0)} documents indexed")
    llm = app.state.llm_handler
    _providers = []
    if llm.gemini_model:
        _providers.append(f"Gemini ({llm.gemini_model_name})")
    if llm.groq_client:
        _providers.append(f"Groq fallback ({llm.groq_model_name})")
    print(f"LLM ready      : {', '.join(_providers) or 'NONE — check API keys'}")
    print("API is ready!  Docs -> http://localhost:8000/docs")
    print("=" * 55)

    yield  # App runs here

    # Cleanup
    del app.state.vector_store
    del app.state.retriever
    del app.state.llm_handler
    print("API shutdown complete.")


# ── FastAPI app ───────────────────────────────────────────────
app = FastAPI(
    title="Gita Wisdom Guide API",
    description=(
        "AI-powered spiritual guidance from the Bhagavad Gita. "
        "Uses RAG (Retrieval-Augmented Generation) to find relevant verses "
        "and generate Krishna-inspired responses via Google Gemini."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
# ALLOWED_ORIGINS env var accepts comma-separated extra origins (e.g. Vercel URL)
import os as _os
_extra = [o.strip() for o in _os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ] + _extra,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes (imported after app is created) ────────────────────
from backend.api.routes import wisdom, verses, health  # noqa: E402

app.include_router(wisdom.router, prefix="/api", tags=["Wisdom"])
app.include_router(verses.router, prefix="/api", tags=["Verses"])
app.include_router(health.router, prefix="/api", tags=["Health"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "Gita Wisdom Guide API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "query_endpoint": "POST /api/query",
    }
