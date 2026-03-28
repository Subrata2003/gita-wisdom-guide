"""
Gita Wisdom Guide — Vector Store

Embedding provider: fastembed  BAAI/bge-small-en-v1.5  (384-dim, ONNX)
Vector DB: ChromaDB (local persistent)

Why fastembed:
  - Uses ONNX Runtime, NOT PyTorch  →  ~150 MB RAM vs ~500 MB for sentence-transformers
  - Fully local, zero API calls, zero rate limits, zero credit card needed
  - Fits comfortably in Render free tier (512 MB)
  - ~24 MB model downloaded once on first use, then cached
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional

import chromadb

_EMBED_MODEL = "BAAI/bge-small-en-v1.5"
_BATCH_SIZE  = 128


class GitaVectorStore:
    def __init__(
        self,
        collection_name: str = "gita_wisdom",
        persist_directory: str = "./vector_db",
    ):
        self.collection_name   = collection_name
        self.persist_directory = persist_directory

        self.client        = chromadb.PersistentClient(path=persist_directory)
        self._embed_model  = None   # lazy-loaded on first embed call
        self.collection    = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Bhagavad Gita verses and wisdom"},
        )

    # ── Embedding helpers ─────────────────────────────────────────────────────

    def _get_model(self):
        if self._embed_model is None:
            from fastembed import TextEmbedding
            self._embed_model = TextEmbedding(model_name=_EMBED_MODEL)
        return self._embed_model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts; returns list of float vectors."""
        model = self._get_model()
        return [emb.tolist() for emb in model.embed(texts)]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Alias used by the indexing pipeline."""
        return self.embed_texts(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single search query."""
        model = self._get_model()
        return next(model.embed([text])).tolist()

    # ── Indexing ──────────────────────────────────────────────────────────────

    def add_documents(self, documents: List[Dict]) -> None:
        texts     = [doc["text"] for doc in documents]
        ids       = [str(uuid.uuid4()) for _ in documents]
        metadatas = []

        for doc in documents:
            meta = {
                "chapter":      str(doc.get("chapter", "")),
                "verse":        str(doc.get("verse", "")),
                "verse_id":     doc.get("verse_id", ""),
                "content_type": doc.get("content_type", "verse"),
                "theme":        doc.get("theme", "general"),
            }
            if "chunk_id" in doc:
                meta["chunk_id"]      = doc["chunk_id"]
                meta["chapter_range"] = doc.get("chapter_range", "")
                meta["verse_range"]   = doc.get("verse_range", "")
            metadatas.append(meta)

        embeddings = self.embed_texts(texts)

        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids,
        )
        print(f"  Added {len(documents)} documents")

    def load_and_index_data(self, data_path: str) -> None:
        """Load processed data JSON and rebuild the entire vector index."""
        with open(data_path, "r", encoding="utf-8") as f:
            documents = json.load(f)

        # Drop and recreate to avoid dimension-mismatch on model switch
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Bhagavad Gita verses and wisdom"},
        )

        for i in range(0, len(documents), _BATCH_SIZE):
            batch = documents[i : i + _BATCH_SIZE]
            self.add_documents(batch)
            print(f"  Progress: {min(i + _BATCH_SIZE, len(documents))}/{len(documents)}")

        print(f"Successfully indexed {len(documents)} documents")

    # ── Search ────────────────────────────────────────────────────────────────

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
        return self.search_similar(query, n_results, {"theme": theme})

    def search_by_chapter(self, query: str, chapter: int, n_results: int = 3) -> Dict:
        return self.search_similar(query, n_results, {"chapter": str(chapter)})

    # ── Info ──────────────────────────────────────────────────────────────────

    def get_collection_info(self) -> Dict:
        return {
            "collection_name": self.collection_name,
            "document_count":  self.collection.count(),
            "embedding_model": _EMBED_MODEL,
        }
