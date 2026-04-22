# Debt Collection Assistant

An AI-powered compliance copilot for debt collection agents. Built with a RAG pipeline to answer questions grounded in real reference documents — FDCPA rules, call scripts, account data, and terminology.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                │
│  ChatWindow → ControlBar → MessageList → ChatInput  │
│  FileUpload ← useChat hook ← api.ts (fetch/SSE)     │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼──────────────────────────────┐
│                   Backend (FastAPI)                  │
│  POST /api/chat → RAG Pipeline                       │
│  POST /api/ingest → Chunker → Embedder → ChromaDB   │
│  GET/PUT /api/config/system-prompt → PromptStore    │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
   ┌──────▼──────┐          ┌───────▼──────┐
   │  ChromaDB   │          │  OpenAI API  │
   │ (vector DB) │          │  embeddings  │
   └─────────────┘          │  + chat      │
                            └──────────────┘
```

**RAG flow:**
1. At startup, 4 reference documents are chunked, embedded, and stored in ChromaDB
2. On each query, the user's question is embedded and top-5 similar chunks are retrieved
3. Retrieved chunks + system prompt + query are sent to the LLM
4. Response streams back via SSE (or returns as JSON in non-streaming mode)

---

## Quick Start (Docker)

```bash
git clone <repo-url>
cd levers-fullstack-ai-task

cp .env.example .env
# Edit .env — set your OPENAI_API_KEY

docker compose up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

On first startup the backend auto-ingests the 4 reference documents. Subsequent restarts skip ingestion (ChromaDB volume persists).

---

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY, set CHROMA_HOST=localhost CHROMA_PORT=8001

# Start ChromaDB first
docker run -p 8001:8000 chromadb/chroma:latest

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev   # Turbopack — http://localhost:3000
```

---

## API Reference

All endpoints are documented at `http://localhost:8000/docs` (Swagger UI).

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Send a query (supports streaming) |
| `POST` | `/api/ingest` | Upload and ingest a `.md` or `.csv` file |
| `GET` | `/api/config/system-prompt` | Get current system prompt |
| `PUT` | `/api/config/system-prompt` | Update system prompt at runtime |
| `DELETE` | `/api/config/system-prompt` | Reset system prompt to default |

### `POST /api/chat`

```json
{
  "query": "What are the permitted calling hours?",
  "model": "gpt-4o-mini",
  "stream": false
}
```

Response:
```json
{
  "answer": "Permitted hours are 8 AM to 9 PM local time...",
  "sources": ["fdcpa_quick_reference.md"],
  "rag_used": true
}
```

Set `"stream": true` to receive an SSE stream (`data: <token>\n\n`, terminated with `data: [DONE]\n\n`).

---

## Linting and Tests

```bash
# Backend
cd backend
source venv/bin/activate
ruff check .
pytest tests/ -v

# Frontend
cd frontend
npm run lint
npm test
```

---

## Design Decisions

### Vector DB — ChromaDB
Zero infrastructure, runs in Docker, persistent volume. Sufficient for this document size. Would switch to Qdrant or pgvector for production workloads.

### Embeddings — `text-embedding-3-small`
Fast and cheap. Our total corpus is ~900 words — quality difference from `text-embedding-3-large` is negligible here.

### Chunking strategy
- **Fixed-size (500 words, 50 overlap)** for FDCPA rules and call scripts — simple prose, safe to split
- **Section-based** for `glossary.md` — contains markdown tables that would be broken by word-boundary splitting
- **CSV → prose conversion** for account data — embeddings work on semantic meaning; raw CSV rows have poor vector representation

### LLM — `gpt-4o-mini` + `o1-mini`
- `gpt-4o-mini`: fast, cheap, supports streaming — default model
- `o1-mini`: chain-of-thought "thinking" model — note: doesn't support streaming or the `system` role (prompt injected as first user message)

### Streaming — SSE
FastAPI `StreamingResponse` with `text/event-stream` media type. Frontend reads with `ReadableStream` + `TextDecoder`. The `X-Accel-Buffering: no` header prevents proxy buffering.

### System Prompt — In-memory singleton
A module-level Python variable in `app/core/prompt_store.py`. Updated at runtime via `PUT /api/config/system-prompt`. No database needed for a single-process server.

### Auto-seeding
On startup, `seed_loader.py` checks `collection.count()`. If zero, ingests all 4 reference files. Skips on subsequent restarts — avoids wasting OpenAI API credits on every container restart.

---

## Known Limitations

- **System prompt is not persisted** — a server restart resets it to default
- **No auth** — any client can query or ingest documents
- **Single ChromaDB collection** — all documents share one namespace; no per-user scoping
- **No document deduplication** — uploading the same file twice creates duplicate chunks (mitigated by `upsert` using filename + index as ID)
- **o1-mini doesn't stream** — the toggle is visible but falls back to a single-chunk response for this model

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers (chat, ingest, config)
│   │   ├── core/         # Config, system prompt store
│   │   ├── models/       # Pydantic schemas
│   │   ├── services/     # RAG pipeline, LLM, embedder, vector store
│   │   └── utils/        # Document loader, seed loader
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # UI components
│   │   ├── hooks/        # useChat
│   │   ├── lib/          # API client
│   │   └── types/        # TypeScript interfaces
│   └── __tests__/
├── rag-reference-data/   # Seed documents (committed)
├── docker-compose.yml
└── .github/workflows/ci.yml
```
