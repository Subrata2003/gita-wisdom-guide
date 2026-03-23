"""
Multi-provider LLM Handler for Gita Wisdom Guide.

Provider priority:
  1. Google Gemini  (primary)
  2. Groq           (automatic fallback on rate-limit / quota errors)

Both providers use the same prompt logic.
Groq uses the OpenAI-compatible chat completions format (system + user messages).
Gemini receives the same content as a single combined prompt.

To swap models: edit DEFAULT_LLM / GROQ_MODEL in .env — no code changes needed.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv

from backend.core.prompts import (
    SPIRITUAL_GUIDE_SYSTEM,
    GREETING_SYSTEM,
    FACTUAL_SYSTEM,
    MENTAL_HEALTH_KEYWORDS,
    MENTAL_HEALTH_DISCLAIMER,
)
from backend.core.query_classifier import QueryType

_ROOT = Path(__file__).parent.parent.parent
load_dotenv(_ROOT / ".env")

# Rate-limit signal phrases — same across all providers
_RATE_LIMIT_SIGNALS = (
    "429", "rate limit", "quota exceeded", "resource exhausted",
    "too many requests", "ratelimitexceeded", "rate_limit_exceeded",
    "tokens per", "requests per",
)


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(s in msg for s in _RATE_LIMIT_SIGNALS)


class EnhancedGitaLLMHandler:
    """
    Wraps Gemini (primary) and Groq (fallback) behind a single interface.

    All public methods return the same Dict shape:
        {response, used_verses, themes, error, provider}
    """

    def __init__(self, model_name: str = None):
        try:
            from backend.config import settings
            self.gemini_model_name = model_name or settings.DEFAULT_LLM
            self.groq_model_name = settings.GROQ_MODEL
            self._google_key = settings.GOOGLE_API_KEY
            self._groq_key = settings.GROQ_API_KEY
        except ImportError:
            self.gemini_model_name = model_name or "gemini-2.5-flash"
            self.groq_model_name = "llama-3.3-70b-versatile"
            self._google_key = os.getenv("GOOGLE_API_KEY", "")
            self._groq_key = os.getenv("GROQ_API_KEY", "")

        self.gemini_model = None
        self.groq_client = None
        self._init_gemini()
        self._init_groq()

    # ─── Initialisation ───────────────────────────────────────────────────────

    def _init_gemini(self):
        if not self._google_key:
            print("WARNING: GOOGLE_API_KEY not set — Gemini disabled.")
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._google_key)
            self.gemini_model = genai.GenerativeModel(self.gemini_model_name)
            print(f"Gemini ready: {self.gemini_model_name}")
        except Exception as e:
            print(f"WARNING: Gemini init failed: {e}")

    def _init_groq(self):
        if not self._groq_key:
            print("INFO: GROQ_API_KEY not set — Groq fallback disabled.")
            return
        try:
            from groq import Groq
            self.groq_client = Groq(api_key=self._groq_key)
            print(f"Groq ready (fallback): {self.groq_model_name}")
        except Exception as e:
            print(f"WARNING: Groq init failed: {e}")

    # ─── Public API ───────────────────────────────────────────────────────────

    def generate_response(self, user_query: str, context: Dict) -> Dict:
        """Full spiritual guidance with RAG context — called for SPIRITUAL queries."""
        if not self._any_provider_ready():
            return self._unavailable_response(context)

        system, user_content = self._build_spiritual_parts(user_query, context)

        try:
            text, provider = self._call_with_fallback(system, user_content)

            if self._needs_mental_health_disclaimer(user_query):
                text += MENTAL_HEALTH_DISCLAIMER

            return {
                "response": text,
                "used_verses": context.get("used_verses", []),
                "themes": context.get("query_themes", []),
                "provider": provider,
                "error": False,
            }
        except Exception as e:
            fallback_text = self._fallback_verse_response(context)
            return {
                "response": fallback_text or f"I encountered difficulty providing guidance: {e}",
                "used_verses": context.get("used_verses", []),
                "themes": context.get("query_themes", []),
                "provider": "none",
                "error": True,
            }

    def generate_typed_response(self, user_query: str, query_type: QueryType) -> Dict:
        """Short responses for GREETING and FACTUAL queries — no RAG context."""
        if not self._any_provider_ready():
            return self._unavailable_response({})

        system = GREETING_SYSTEM if query_type == QueryType.GREETING else FACTUAL_SYSTEM
        user_content = f'The seeker asks: "{user_query}"'

        try:
            text, provider = self._call_with_fallback(system, user_content)
            return {
                "response": text,
                "used_verses": [],
                "themes": [],
                "provider": provider,
                "error": False,
            }
        except Exception as e:
            return {
                "response": f"I encountered difficulty responding: {e}",
                "used_verses": [],
                "themes": [],
                "provider": "none",
                "error": True,
            }

    # ─── Provider dispatch ────────────────────────────────────────────────────

    def _call_with_fallback(self, system: str, user_content: str) -> Tuple[str, str]:
        """
        Try Gemini first. On rate-limit → switch to Groq.
        Returns (response_text, provider_name).
        """
        # 1. Try Gemini
        if self.gemini_model:
            try:
                text = self._call_gemini(system, user_content)
                return text, "gemini"
            except Exception as e:
                if _is_rate_limit(e):
                    print(f"Gemini rate limit hit — switching to Groq. ({type(e).__name__})")
                else:
                    raise  # Non-rate-limit Gemini error — propagate

        # 2. Groq fallback
        if self.groq_client:
            text = self._call_groq(system, user_content)
            return text, "groq"

        raise RuntimeError(
            "All LLM providers are unavailable. "
            "Check GOOGLE_API_KEY and GROQ_API_KEY in your .env file."
        )

    def _call_gemini(self, system: str, user_content: str) -> str:
        full_prompt = f"{system}\n\n{user_content}"
        response = self.gemini_model.generate_content(full_prompt)
        return response.text

    def _call_groq(self, system: str, user_content: str) -> str:
        completion = self.groq_client.chat.completions.create(
            model=self.groq_model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_content},
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return completion.choices[0].message.content

    # ─── Streaming generators ─────────────────────────────────────────────────

    def _stream_gemini(self, system: str, user_content: str):
        """Sync generator — yields text chunks from Gemini streaming API."""
        full_prompt = f"{system}\n\n{user_content}"
        response = self.gemini_model.generate_content(full_prompt, stream=True)
        for chunk in response:
            if hasattr(chunk, "text") and chunk.text:
                yield chunk.text

    def _stream_groq(self, system: str, user_content: str):
        """Sync generator — yields text chunks from Groq streaming API."""
        stream = self.groq_client.chat.completions.create(
            model=self.groq_model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_content},
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _stream_with_fallback(self, system: str, user_content: str):
        """
        Sync generator — tries Gemini first, falls back to Groq on rate-limit.
        If Gemini fails before the first token, Groq takes over seamlessly.
        If Gemini fails mid-stream, yields an interruption note.
        """
        first_yielded = False

        if self.gemini_model:
            try:
                for chunk in self._stream_gemini(system, user_content):
                    first_yielded = True
                    yield chunk
                return
            except Exception as e:
                if _is_rate_limit(e) and not first_yielded and self.groq_client:
                    print(f"Gemini rate-limit on stream — switching to Groq. ({type(e).__name__})")
                    # fall through to Groq below
                elif first_yielded:
                    yield "\n\n*(Response was interrupted — please try again.)*"
                    return
                else:
                    raise

        if self.groq_client:
            yield from self._stream_groq(system, user_content)
            return

        raise RuntimeError(
            "All LLM providers unavailable. Check GOOGLE_API_KEY / GROQ_API_KEY in .env."
        )

    def stream_response(self, user_query: str, context: Dict):
        """Public streaming generator for SPIRITUAL queries (with RAG context)."""
        system, user_content = self._build_spiritual_parts(user_query, context)
        yield from self._stream_with_fallback(system, user_content)

    def stream_typed_response(self, user_query: str, query_type: QueryType):
        """Public streaming generator for GREETING / FACTUAL queries."""
        system = GREETING_SYSTEM if query_type == QueryType.GREETING else FACTUAL_SYSTEM
        user_content = f'The seeker asks: "{user_query}"'
        yield from self._stream_with_fallback(system, user_content)

    # ─── Prompt builders ──────────────────────────────────────────────────────

    def _build_spiritual_parts(self, user_query: str, context: Dict) -> Tuple[str, str]:
        """Returns (system_prompt, user_content) for the spiritual guidance flow."""
        verses_text = context.get("formatted_context", "")
        themes = context.get("query_themes", [])
        conversation_context = context.get("conversation_context", "")

        conv_block = ""
        if conversation_context:
            conv_block = (
                "\n--- PRIOR CONVERSATION (for continuity, do not repeat verbatim) ---\n"
                f"{conversation_context}\n"
                "--- END PRIOR CONVERSATION ---\n"
            )

        themes_str = ", ".join(t.title() for t in themes) if themes else "General Wisdom"

        user_content = f"""{conv_block}
THE SEEKER'S QUESTION:
"{user_query}"

RELEVANT TEACHINGS FROM THE BHAGAVAD GITA:
{verses_text if verses_text else "(Draw from your general knowledge of the Gita's teachings)"}

SPIRITUAL THEMES IN THIS QUERY: {themes_str}

Now speak your guidance. Be specific, warm, and rooted in the verses above.
Begin directly with acknowledging the seeker — do not start with "I" or "Dear seeker"."""

        return SPIRITUAL_GUIDE_SYSTEM, user_content

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _any_provider_ready(self) -> bool:
        return self.gemini_model is not None or self.groq_client is not None

    def _needs_mental_health_disclaimer(self, query: str) -> bool:
        q = query.lower()
        return any(kw in q for kw in MENTAL_HEALTH_KEYWORDS)

    def _unavailable_response(self, context: Dict) -> Dict:
        return {
            "response": (
                "The wisdom service is not available right now. "
                "Please ensure at least one of GOOGLE_API_KEY or GROQ_API_KEY is set correctly."
            ),
            "error": True,
            "used_verses": context.get("used_verses", []),
            "themes": context.get("query_themes", []),
            "provider": "none",
        }

    def _fallback_verse_response(self, context: Dict) -> Optional[str]:
        verses = context.get("used_verses", [])
        if not verses:
            return None
        v = verses[0]
        return (
            f"The Bhagavad Gita offers this teaching:\n\n"
            f"**Chapter {v['chapter']}, Verse {v['verse']}**: {v['text']}\n\n"
            f"Reflect on this teaching with patience — the Gita illuminates every challenge."
        )
