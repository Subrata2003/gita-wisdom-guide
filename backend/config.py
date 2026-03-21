import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")


def _abs(env_key: str, default: Path) -> str:
    """Return an absolute path — resolve relative paths against ROOT_DIR."""
    raw = os.getenv(env_key, "")
    if not raw:
        return str(default)
    p = Path(raw)
    return str(p) if p.is_absolute() else str(ROOT_DIR / p)


class Settings:
    # ── LLM providers ────────────────────────────────────────────────────────
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Primary Gemini model — gemini-3.1-flash-lite-preview = 500 RPD / 15 RPM (free tier)
    DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "gemini-3.1-flash-lite-preview")
    # Groq fallback model — used automatically when Gemini hits rate limits
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── Vector store ─────────────────────────────────────────────────────────
    VECTOR_DB_PATH: str = _abs("VECTOR_DB_PATH", ROOT_DIR / "vector_db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "gita_wisdom")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # ── Retrieval ─────────────────────────────────────────────────────────────
    MAX_CONTEXT_LENGTH: int = int(os.getenv("MAX_CONTEXT_LENGTH", "3500"))
    MAX_RESULTS: int = int(os.getenv("MAX_RESULTS", "10"))
    RELEVANCE_THRESHOLD: float = 0.20

    # ── Misc ──────────────────────────────────────────────────────────────────
    DATA_PATH: str = str(ROOT_DIR / "data" / "processed_gita_data.json")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ROOT_DIR: Path = ROOT_DIR


settings = Settings()
