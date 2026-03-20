from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid


class SessionManager:
    """
    In-memory session manager for conversation history.
    Stores the last N queries per session with automatic TTL cleanup.
    """

    def __init__(self, max_history: int = 10, session_ttl_hours: int = 2):
        self.sessions: Dict[str, Dict] = {}
        self.max_history = max_history
        self.session_ttl = timedelta(hours=session_ttl_hours)

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        self._cleanup_expired()
        session = self.sessions.get(session_id)
        if session:
            session["last_accessed"] = datetime.now()
        return session

    def add_to_history(
        self,
        session_id: str,
        query: str,
        response: str,
        verses: List[Dict],
        themes: List[str],
    ) -> str:
        session = self.get_session(session_id)
        if not session:
            session_id = self.create_session()
            session = self.sessions[session_id]

        entry = {
            "query": query,
            "response": response,
            "verses": [
                {"chapter": v.get("chapter"), "verse": v.get("verse"), "verse_id": v.get("verse_id")}
                for v in verses
            ],
            "themes": themes,
            "timestamp": datetime.now().isoformat(),
        }

        session["history"].append(entry)

        # Keep only the last max_history entries
        if len(session["history"]) > self.max_history:
            session["history"] = session["history"][-self.max_history :]

        return session_id

    def get_history(self, session_id: str) -> List[Dict]:
        session = self.get_session(session_id)
        return session["history"] if session else []

    def get_conversation_context(self, session_id: str, last_n: int = 3) -> str:
        """Format recent history for LLM context injection."""
        history = self.get_history(session_id)
        if not history:
            return ""

        recent = history[-last_n:]
        context_parts = []
        for entry in recent:
            context_parts.append(f"Seeker asked: {entry['query']}")
            # Truncate long responses so they don't bloat the prompt
            short_response = entry["response"][:300] + "..." if len(entry["response"]) > 300 else entry["response"]
            context_parts.append(f"Guidance given: {short_response}")

        return "\n".join(context_parts)

    def delete_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def _cleanup_expired(self):
        now = datetime.now()
        expired = [
            sid
            for sid, session in self.sessions.items()
            if now - session["last_accessed"] > self.session_ttl
        ]
        for sid in expired:
            del self.sessions[sid]

    def get_stats(self) -> Dict:
        return {
            "active_sessions": len(self.sessions),
            "ttl_hours": self.session_ttl.seconds // 3600,
        }
