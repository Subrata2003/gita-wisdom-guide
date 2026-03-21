"""
Gita Wisdom Guide — First-time setup
Run once before starting the backend for the first time:
    python setup.py

What this does:
1. Processes raw Gita verses into structured documents
2. Creates and indexes the ChromaDB vector database
3. Verifies the system is ready
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def step(msg: str):
    print(f"\n>>> {msg}")


def check_env():
    step("Checking environment")
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or api_key == "your_google_api_key_here":
        print("  ERROR: GOOGLE_API_KEY is not set in .env")
        print("  Gemini embeddings require this key. Get one at https://aistudio.google.com/")
        sys.exit(1)
    else:
        print(f"  GOOGLE_API_KEY    : set ({api_key[:8]}...)")

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    print(f"  Embedding model   : {os.getenv('EMBEDDING_MODEL', 'models/gemini-embedding-001')}")
    print(f"  LLM model         : {os.getenv('DEFAULT_LLM', 'gemini-3.1-flash-lite-preview')}")


def process_data():
    step("Processing Gita verses")
    from data_processor import GitaDataProcessor

    raw_path = ROOT / "data" / "reformatted_bhagavad_gita.json"
    out_path = ROOT / "data" / "processed_gita_data.json"

    if not raw_path.exists():
        print(f"  ERROR: {raw_path} not found.")
        sys.exit(1)

    if out_path.exists():
        print(f"  processed_gita_data.json already exists — skipping re-processing.")
        print("  (Delete data/processed_gita_data.json to force re-processing)")
        return

    processor = GitaDataProcessor()
    processor.process_complete_dataset(str(raw_path), str(out_path))
    stats = processor.get_statistics()
    print(f"  Verses processed : {stats['total_verses']}")
    print(f"  Chunks created   : {stats['total_chunks']}")
    print(f"  Chapters         : {stats['total_chapters']}")


def build_vector_store(force: bool = False):
    step("Building vector database")
    import shutil
    from vector_store import GitaVectorStore
    from backend.config import settings

    processed_path = ROOT / "data" / "processed_gita_data.json"
    if not processed_path.exists():
        print("  ERROR: processed_gita_data.json not found. Run process_data() first.")
        sys.exit(1)

    # Force-delete existing DB when --rebuild is passed
    if force and Path(settings.VECTOR_DB_PATH).exists():
        shutil.rmtree(settings.VECTOR_DB_PATH)
        print(f"  Removed old vector_db at {settings.VECTOR_DB_PATH}")

    vs = GitaVectorStore(
        collection_name=settings.COLLECTION_NAME,
        persist_directory=settings.VECTOR_DB_PATH,
    )
    existing = vs.get_collection_info().get("document_count", 0)

    if existing > 0 and not force:
        print(f"  Vector store already has {existing} documents — skipping.")
        print("  Run  python setup.py --rebuild  to force a full re-index.")
        return

    print(f"  Indexing {processed_path} into ChromaDB...")
    print("  Using Gemini Embedding API — this takes ~8-10 min for 854 docs.")
    vs.load_and_index_data(str(processed_path))
    final_count = vs.get_collection_info().get("document_count", 0)
    print(f"  Indexed {final_count} documents into {settings.VECTOR_DB_PATH}")


def verify():
    step("Verifying system")
    from vector_store import GitaVectorStore
    from backend.config import settings
    from backend.core.enhanced_retrieval import EnhancedGitaRetriever

    vs = GitaVectorStore(
        collection_name=settings.COLLECTION_NAME,
        persist_directory=settings.VECTOR_DB_PATH,
    )
    info = vs.get_collection_info()
    print(f"  Documents  : {info['document_count']}")

    retriever = EnhancedGitaRetriever(vs)
    test_q = "How to find inner peace?"
    results = retriever.retrieve_relevant_verses(test_q, max_results=3)
    print(f"  Test query : '{test_q}'")
    print(f"  Retrieved  : {len(results)} verses (scores: {[r['relevance_score'] for r in results]})")

    if not results:
        print("  WARNING: No results returned — something may be wrong with the index.")
    else:
        print("  System ready!")


if __name__ == "__main__":
    rebuild = "--rebuild" in sys.argv

    print("=" * 55)
    print("  Gita Wisdom Guide — Setup" + (" (REBUILD)" if rebuild else ""))
    print("=" * 55)

    check_env()
    process_data()
    build_vector_store(force=rebuild)
    verify()

    print("\n" + "=" * 55)
    print("  Setup complete!")
    print("  Start the backend : start_backend.bat")
    print("  Start the frontend: start_frontend.bat")
    print("=" * 55)
