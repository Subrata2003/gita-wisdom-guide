"""
Enhanced LLM Handler for Gita Wisdom Guide.

Improvements over original:
- Structured system prompt with clear persona and constraints
- Rich verse context formatting (chapter/verse labels)
- Conversation history injection for continuity
- Better mental health keyword detection
- Graceful API error handling with fallback
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

_ROOT = Path(__file__).parent.parent.parent
load_dotenv(_ROOT / ".env")

MENTAL_HEALTH_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "want to die",
    "severely depressed",
    "hopeless",
    "can't go on",
    "cannot go on",
    "worthless",
    "self harm",
    "hurt myself",
    "no reason to live",
]

SYSTEM_PROMPT = """You are a compassionate spiritual guide who embodies the wisdom of the Bhagavad Gita, speaking with the gentle yet firm authority of Krishna's teachings to Arjuna.

YOUR PERSONA:
- Wise, warm, and deeply empathetic — you understand human suffering from the inside
- You speak as a trusted friend and guide, not as a distant academic
- You honour the seeker's emotional reality before offering wisdom

YOUR APPROACH:
1. Begin by truly acknowledging the seeker's struggle (1-2 sentences of genuine empathy)
2. Draw from the specific verses provided — cite them naturally, e.g. "As Krishna tells Arjuna in Chapter 2, Verse 47..."
3. Connect ancient wisdom to the seeker's modern situation concretely and practically
4. Offer 2-3 actionable spiritual practices or perspective shifts
5. Close with an uplifting reminder of the seeker's inherent strength and potential

YOUR TONE:
- Warm and personal, not preachy or clinical
- Hopeful without dismissing real pain
- Grounded — rooted in specific teachings, not vague platitudes
- Use "you" to speak directly to the seeker

CONSTRAINTS:
- Never simply paraphrase verses without applying them to the situation
- Avoid generic spiritual clichés that could apply to anyone
- If the query involves serious mental health concerns, acknowledge the wisdom AND gently encourage professional support
- Keep responses focused and readable — avoid walls of text; use short paragraphs"""


class EnhancedGitaLLMHandler:
    def __init__(self, model_name: str = None):
        try:
            from backend.config import settings
            self.model_name = model_name or settings.DEFAULT_LLM
        except ImportError:
            self.model_name = model_name or "gemini-2.5-flash"

        self.model = None
        self._init_model()

    def _init_model(self):
        try:
            import google.generativeai as genai

            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("WARNING: GOOGLE_API_KEY not set. LLM will not function.")
                return

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            print(f"LLM initialized: {self.model_name}")
        except Exception as e:
            print(f"WARNING: Failed to initialize LLM: {e}")

    def create_response_prompt(self, user_query: str, context: Dict) -> str:
        verses_text = context.get("formatted_context", "")
        themes = context.get("query_themes", [])
        conversation_context = context.get("conversation_context", "")

        # Build conversation context block
        conv_block = ""
        if conversation_context:
            conv_block = f"""
--- PRIOR CONVERSATION (for continuity, do not repeat verbatim) ---
{conversation_context}
--- END PRIOR CONVERSATION ---
"""

        themes_str = ", ".join(t.title() for t in themes) if themes else "General Wisdom"

        prompt = f"""{SYSTEM_PROMPT}
{conv_block}
THE SEEKER'S QUESTION:
"{user_query}"

RELEVANT TEACHINGS FROM THE BHAGAVAD GITA:
{verses_text if verses_text else "(Draw from your general knowledge of the Gita's teachings)"}

SPIRITUAL THEMES IN THIS QUERY: {themes_str}

Now provide your guidance. Be specific, warm, and grounded in the verses above.
Begin directly with acknowledging the seeker — do not start with "I" or a greeting like "Dear seeker"."""

        return prompt

    def generate_response(self, user_query: str, context: Dict) -> Dict:
        if not self.model:
            return {
                "response": (
                    "The wisdom service is not available right now. "
                    "Please ensure the GOOGLE_API_KEY is set correctly."
                ),
                "error": True,
                "used_verses": [],
                "themes": [],
            }

        try:
            prompt = self.create_response_prompt(user_query, context)
            response = self.model.generate_content(prompt)
            response_text = response.text

            if self._needs_mental_health_disclaimer(user_query):
                response_text += (
                    "\n\n---\n"
                    "*While this ancient wisdom offers profound comfort, if you are experiencing "
                    "persistent distress or thoughts of self-harm, please reach out to a mental "
                    "health professional or a crisis helpline. You deserve both spiritual and "
                    "professional support — seeking help is an act of courage, not weakness.*"
                )

            return {
                "response": response_text,
                "used_verses": context.get("used_verses", []),
                "themes": context.get("query_themes", []),
                "error": False,
            }

        except Exception as e:
            error_msg = str(e)
            # Provide a graceful degraded response
            fallback = self._fallback_response(user_query, context)
            return {
                "response": fallback or f"I encountered difficulty providing guidance: {error_msg}",
                "error": True,
                "used_verses": context.get("used_verses", []),
                "themes": context.get("query_themes", []),
            }

    def _fallback_response(self, query: str, context: Dict) -> str:
        """Return a basic response using verse text if LLM fails."""
        verses = context.get("used_verses", [])
        if not verses:
            return ""

        verse = verses[0]
        return (
            f"The Bhagavad Gita offers this teaching for your situation:\n\n"
            f"**Chapter {verse['chapter']}, Verse {verse['verse']}**: {verse['text']}\n\n"
            f"Reflect on this teaching in relation to what you are experiencing. "
            f"The Gita's wisdom, when applied with patience, illuminates every challenge."
        )

    def _needs_mental_health_disclaimer(self, query: str) -> bool:
        query_lower = query.lower()
        return any(kw in query_lower for kw in MENTAL_HEALTH_KEYWORDS)

    def generate_simple_response(self, user_query: str) -> str:
        """Fallback: generate a response without retrieval context."""
        if not self.model:
            return "I apologize, but I cannot provide guidance at this moment."

        simple_prompt = f"""{SYSTEM_PROMPT}

The seeker asks: "{user_query}"

Draw from your knowledge of the Bhagavad Gita's teachings to provide compassionate,
practical guidance — even without specific verse citations."""

        try:
            response = self.model.generate_content(simple_prompt)
            return response.text
        except Exception as e:
            return f"I encountered difficulty providing guidance: {str(e)}"
