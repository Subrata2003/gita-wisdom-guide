"""
Vector store for Gita Wisdom Guide.

Embedding backend: Google Gemini Embedding API (gemini-embedding-001)
  - No local ML model — zero RAM overhead at runtime
  - Batched API calls for indexing
  - task_type differentiation: retrieval_document (index) vs retrieval_query (search)
  - Automatic retry on transient rate-limit errors
"""

import json
import os
import time
import uuid
from typing import Dict, List, Optional

import chromadb


def _gemini_embed_one(text: str, task_type: str) -> List[float]:
    """
    Embed a single text via Gemini Embedding API.
    Retries once on rate-limit with a 62-second back-off (resets the per-minute window).
    """
    import google.generativeai as genai

    # Auto-configure if not already done (e.g. when called from setup.py)
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)

    model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    # Normalise: always needs models/ prefix for the Gemini API
    if not model.startswith("models/") and not model.startswith("tunedModels/"):
        model = f"models/{model}"

    for attempt in range(2):
        try:
            result = genai.embed_content(
                model=model,
                content=text,
                task_type=task_type,
            )
            return result["embedding"]
        except Exception as e:
            msg = str(e).lower()
            is_rate_limit = any(s in msg for s in ("429", "quota", "rate limit", "resource exhausted"))
            if is_rate_limit and attempt == 0:
                print("  Embedding rate limit — waiting 62s...")
                time.sleep(62)
                continue
            raise


def _gemini_embed(texts: List[str], task_type: str) -> List[List[float]]:
    """Embed a list of texts, one call each, with pacing to stay under 100 RPM."""
    results = []
    for i, t in enumerate(texts):
        results.append(_gemini_embed_one(t, task_type))
        if i < len(texts) - 1:
            time.sleep(0.7)   # ~85 RPM — safely under the 100 RPM free-tier limit
    return results


class GitaVectorStore:
    def __init__(
        self,
        collection_name: str = "gita_wisdom",
        persist_directory: str = "./vector_db",
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        self.client = chromadb.PersistentClient(path=persist_directory)

        # No embedding function passed — we compute embeddings manually and inject them.
        # This gives us full control over task_type (document vs query).
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Bhagavad Gita verses and wisdom"},
        )

    # ─── Embedding helpers ────────────────────────────────────────────────────

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed texts for indexing (task_type=retrieval_document)."""
        return _gemini_embed(texts, task_type="retrieval_document")

    def embed_query(self, text: str) -> List[float]:
        """Embed a single search query (task_type=retrieval_query)."""
        return _gemini_embed([text], task_type="retrieval_query")[0]

    # kept for backward compatibility with any callers using embed_texts
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embed_documents(texts)

    # ─── Indexing ─────────────────────────────────────────────────────────────

    def add_documents(self, documents: List[Dict]) -> None:
        texts, metadatas, ids = [], [], []

        for doc in documents:
            ids.append(str(uuid.uuid4()))
            texts.append(doc["text"])

            metadata = {
                "chapter":      str(doc.get("chapter", "")),
                "verse":        str(doc.get("verse", "")),
                "verse_id":     doc.get("verse_id", ""),
                "content_type": doc.get("content_type", "verse"),
                "theme":        doc.get("theme", "general"),
            }
            if "chunk_id" in doc:
                metadata["chunk_id"]      = doc["chunk_id"]
                metadata["chapter_range"] = doc.get("chapter_range", "")
                metadata["verse_range"]   = doc.get("verse_range", "")

            metadatas.append(metadata)

        embeddings = self.embed_documents(texts)

        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids,
        )
        print(f"  Indexed {len(documents)} documents")

    def load_and_index_data(self, data_path: str) -> None:
        """Load processed JSON data, rebuild the collection from scratch."""
        with open(data_path, "r", encoding="utf-8") as f:
            documents = json.load(f)

        # Rebuild collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Bhagavad Gita verses and wisdom"},
        )

        batch_size = 50   # conservative batch size to stay within token limits
        total = len(documents)
        for i in range(0, total, batch_size):
            batch = documents[i : i + batch_size]
            print(f"Indexing batch {i // batch_size + 1}/{-(-total // batch_size)}...")
            self.add_documents(batch)

        print(f"Successfully indexed {total} documents using Gemini embeddings.")

    # ─── Search ───────────────────────────────────────────────────────────────

    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> Dict:
        query_embedding = self.embed_query(query)

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )

    def search_by_theme(self, query: str, theme: str, n_results: int = 3) -> Dict:
        return self.search_similar(query, n_results, filter_metadata={"theme": theme})

    def search_by_chapter(self, query: str, chapter: int, n_results: int = 3) -> Dict:
        return self.search_similar(query, n_results, filter_metadata={"chapter": str(chapter)})

    # ─── Info ─────────────────────────────────────────────────────────────────

    def get_collection_info(self) -> Dict:
        model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
        return {
            "collection_name": self.collection_name,
            "document_count":  self.collection.count(),
            "embedding_model": model,
        }
