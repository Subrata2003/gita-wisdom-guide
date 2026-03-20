# Gita Wisdom Guide

> *"You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions."*
> — Bhagavad Gita 2.47

An AI-powered spiritual guidance application built on the Bhagavad Gita. Ask life questions in plain language and receive thoughtful, verse-backed responses inspired by Krishna's teachings — powered by a RAG pipeline and Google Gemini.

---

## Architecture

```
┌─────────────────────────┐        ┌──────────────────────────────────┐
│   React Frontend        │  HTTP  │   FastAPI Backend  :8000          │
│   Vite + Tailwind CSS   │◄──────►│                                  │
│   localhost:5173        │        │  ┌────────────────────────────┐  │
└─────────────────────────┘        │  │  Enhanced RAG Engine       │  │
                                   │  │  • Query expansion         │  │
                                   │  │  • Multi-theme detection   │  │
                                   │  │  • ChromaDB vector search  │  │
                                   │  │  • Relevance thresholding  │  │
                                   │  │  • Conversation memory     │  │
                                   │  └────────────┬───────────────┘  │
                                   │               │                  │
                                   │  ┌────────────▼───────────────┐  │
                                   │  │  Google Gemini LLM         │  │
                                   │  │  Krishna-style prompt      │  │
                                   │  └────────────────────────────┘  │
                                   └──────────────────────────────────┘
```

## Key Features

- **Chat Interface** — conversational UI with session memory across turns
- **Enhanced RAG** — query expansion, multi-theme detection, correct similarity scoring
- **Verse References** — every response cites specific chapters and verses with relevance scores
- **Theme Explorer** — browse all 8 Gita themes (Duty, Detachment, Knowledge, Devotion, Action, Soul, Peace, Meditation)
- **REST API** — fully documented FastAPI backend with Swagger UI
- **Spiritual UI** — dark theme with animated mandala, saffron/gold palette

---

## Project Structure

```
gita-wisdom-guide/
├── backend/                      # FastAPI application
│   ├── main.py                   # App entry, lifespan startup, CORS
│   ├── config.py                 # Settings from .env (paths always absolute)
│   ├── api/routes/
│   │   ├── wisdom.py             # POST /api/query
│   │   ├── verses.py             # GET /api/themes, /api/verses/search
│   │   └── health.py             # GET /api/health
│   ├── core/
│   │   ├── enhanced_retrieval.py # RAG engine
│   │   ├── llm_handler.py        # Gemini prompt + response
│   │   └── session_manager.py    # In-memory conversation history
│   └── models/schemas.py         # Pydantic request/response models
│
├── frontend/                     # React + Vite application
│   └── src/
│       ├── App.jsx               # Root — state, session, scroll
│       ├── components/
│       │   ├── ChatMessage.jsx   # Markdown bubbles + verse accordion
│       │   ├── QueryInput.jsx    # Auto-resize textarea
│       │   ├── VerseCard.jsx     # Verse with relevance bar
│       │   ├── Sidebar.jsx       # Themes, samples, session info
│       │   ├── Header.jsx        # Logo + status pill
│       │   ├── ThemeBadge.jsx    # Colour-coded theme tag
│       │   └── MandalaBackground.jsx  # Animated SVG mandala
│       └── services/api.js       # Axios client (proxied to :8000)
│
├── src/                          # Shared Python library
│   ├── vector_store.py           # ChromaDB wrapper
│   └── data_processor.py         # Raw JSON → structured docs + chunks
│
├── data/
│   ├── reformatted_bhagavad_gita.json  # Raw source (700 verses, 18 chapters)
│   ├── processed_gita_data.json        # Processed + chunked (~854 documents)
│   └── bhagavad_gita_verses.csv        # CSV format
│
├── setup.py                      # One-time data processing + indexing
├── requirements.txt              # Python dependencies
├── start_backend.bat             # Windows: launch FastAPI backend
└── start_frontend.bat            # Windows: launch React frontend
```

---

## Quick Start

### Prerequisites

- Python with pip (Anaconda recommended)
- Node.js 18+
- Google Gemini API key — free at [aistudio.google.com](https://aistudio.google.com/)

### 1 — Configure environment

```bash
cp .env.example .env
# Open .env and set GOOGLE_API_KEY=your_key_here
```

### 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3 — Build the vector database *(first time only)*

```bash
python setup.py
```

### 4 — Start the backend

```bash
# Windows
start_backend.bat

# or directly
uvicorn backend.main:app --reload --port 8000
```

### 5 — Start the frontend

```bash
# Windows
start_frontend.bat

# or directly
cd frontend && npm install && npm run dev
```

Open **http://localhost:5173** in your browser.
Swagger API docs: **http://localhost:8000/docs**

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query` | Get spiritual guidance for a question |
| `GET`  | `/api/health` | System status and document count |
| `GET`  | `/api/themes` | All spiritual themes with descriptions |
| `GET`  | `/api/verses/search?q=...` | Semantic verse search |
| `GET`  | `/api/verses/search?theme=...` | Filter verses by theme |
| `GET`  | `/api/verses/search?chapter=...` | Filter verses by chapter (1–18) |
| `GET`  | `/api/session/{id}/history` | Conversation history for a session |
| `DELETE` | `/api/session/{id}` | Clear a session |

**Example:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "I feel lost and don'\''t know my purpose"}'
```

---

## RAG Pipeline Improvements

| Aspect | What changed |
|--------|-------------|
| **Relevance scoring** | Fixed formula: `1 - dist²/2` for L2 distance (old `1 - dist` gave negative scores) |
| **Theme detection** | Scores *all* matching themes by frequency, not first-match-wins |
| **Query expansion** | Appends spiritual synonyms to improve recall (e.g. `stress → stress burden restless disturbed overwhelm`) |
| **Multi-strategy search** | Theme-filtered + general (expanded) + general (original) combined and deduplicated |
| **Score threshold** | Filters results below 0.20 relevance to avoid hallucination from irrelevant context |
| **Deduplication** | By both `verse_id` and text prefix — catches overlapping chunks |
| **Context window** | Increased from 2 000 to 3 500 characters |
| **Conversation context** | Last 3 Q&A pairs injected into each LLM prompt for continuity |
| **Prompt engineering** | Structured system prompt with explicit persona, tone, format, and constraints |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite 5, Tailwind CSS 3 |
| Backend | FastAPI 0.116, Uvicorn |
| Vector DB | ChromaDB (persistent local) |
| Embeddings | `all-MiniLM-L6-v2` — sentence-transformers |
| LLM | Google Gemini `gemini-2.5-flash` |
| Session | In-memory per-process (UUID keyed) |

---

## Roadmap

- [ ] User authentication (JWT) + persistent login
- [ ] Database-backed session storage (PostgreSQL / SQLite)
- [ ] Conversation history UI in sidebar
- [ ] Verse bookmarking and personal notes
- [ ] Chapter browser page

---

## License

MIT — see [LICENSE](LICENSE)
Built with ❤️ by **Subrata Bhuin**

