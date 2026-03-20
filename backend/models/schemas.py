from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None


class VerseInfo(BaseModel):
    chapter: int
    verse: int
    text: str
    theme: str
    verse_id: str
    relevance_score: float


class WisdomResponse(BaseModel):
    response: str
    used_verses: List[VerseInfo]
    themes: List[str]
    session_id: str
    error: bool = False


class HealthResponse(BaseModel):
    status: str
    document_count: int
    embedding_model: str
    version: str


class SessionHistoryEntry(BaseModel):
    query: str
    response: str
    themes: List[str]
    timestamp: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    history: List[SessionHistoryEntry]


class VersesSearchResponse(BaseModel):
    verses: List[dict]
    total: int
