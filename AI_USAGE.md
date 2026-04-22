# AI Usage Disclosure

## Tools Used

- **Claude Code (claude-sonnet-4-6)** — used throughout the entire implementation via the Claude Code CLI

## Scope

Claude Code assisted with generating the full codebase from a detailed implementation plan I authored. This includes:

- Backend: FastAPI structure, all service files (chunker, embedder, vector store, LLM, retriever, RAG pipeline), API endpoints, seed loader, and tests
- Frontend: Next.js component architecture, hooks, API client, Jest test setup
- Infrastructure: `docker-compose.yml`, Dockerfiles, GitHub Actions CI

## Key Prompts and Decisions

The core implementation plan was written before AI assistance and lives in this repository as the full roadmap. Key decisions made in the plan:

- **No LangChain/LangGraph** — direct OpenAI SDK calls for clarity and auditability
- **ChromaDB over hosted vector DBs** — zero infrastructure, runs in Docker
- **Section-based chunking for glossary** — glossary has markdown tables that break if split mid-row
- **Prose conversion for CSV** — embeddings work better on natural language than raw CSV rows
- **o1-mini system prompt workaround** — o1 models reject the `system` role; prompt injected as first user message

## Human Review

- All generated code was reviewed line-by-line
- Tests were written to verify specific behaviors (overlap, section splitting, empty store handling, API contracts)
- Linting was run after generation and all errors were fixed
- The build was verified end-to-end (`npm run build`, `pytest`, `ruff check`)
- Design decisions and architecture were authored by me; Claude implemented them

## Understanding

I am prepared to explain any part of this codebase — the chunking strategy, the SSE streaming implementation, the ChromaDB singleton, the o1 message format workaround, or the React hooks architecture.
