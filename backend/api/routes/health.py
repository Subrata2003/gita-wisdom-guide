from fastapi import APIRouter, Request
from backend.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Check API health and vector store status."""
    vector_store = getattr(request.app.state, "vector_store", None)

    if not vector_store:
        return HealthResponse(
            status="initializing",
            document_count=0,
            embedding_model="unknown",
            version="2.0.0",
        )

    info = vector_store.get_collection_info()
    return HealthResponse(
        status="healthy",
        document_count=info.get("document_count", 0),
        embedding_model=info.get("embedding_model", "all-MiniLM-L6-v2"),
        version="2.0.0",
    )
