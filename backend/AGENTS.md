# Backend Agent Instructions

Read the root `AGENTS.md` first. This file covers backend-specific rules.

## Layout

```text
backend/
├── alembic/              # migrations (SQLAlchemy models are the source of truth)
├── app/
│   ├── api/              # FastAPI routers (auth, chat) — thin, no business logic
│   ├── auth/             # token verification, demo JWT
│   ├── chat/             # orchestrator, message conversion, SSE streaming
│   ├── assistant/        # agent boundary: tools, deps, outputs, instructions
│   ├── retrieval/        # hybrid search: queries, keywords, fusion, retriever
│   ├── grounding/        # fail-closed citation validation
│   ├── database/         # models, session, persistence helpers
│   └── schemas/          # request/response models
├── ingest/               # corpus pipeline (HTML → chunks → embeddings)
├── scripts/              # smoke scripts
└── tests/                # unit tests (no DB or network required)
```

## Rules

- **Layering:** `api → chat → assistant → retrieval/grounding → database`. Never import upward. `ingest` may use `app.config` and `app.database` only.
- **SQLAlchemy models are the schema source of truth.** Schema changes: edit models → `alembic revision --autogenerate` → hand-finish `vector`/tsvector/index DDL → `alembic upgrade head`.
- **The turn registry is the citation allowlist.** Every tool result registers passages; the grounding validator rejects citations outside it. Don't bypass either.
- **Streaming protocol:** AI SDK v5 UI message stream (`start`, `text-start/delta/end`, `data-citation`, `data-status`, `finish`, `error`). Don't invent event types.
- **Real vs demo mode:** branch at the provider boundary only (`embeddings`, `keywords`, `agent`, `grounding judge`, `auth`). Business logic must be mode-agnostic. Never let demo fallbacks hide missing real-mode config — startup should fail loudly when real-mode env is incomplete.
- **Sync DB access:** SQLAlchemy sessions are sync. In async routes, wrap DB work with `run_in_threadpool`; the orchestrator runs the agent in `asyncio.to_thread`.
- **Tests** must not need Postgres, OpenAI, or Supabase. Mock at the provider boundary.

## Commands

```bash
uv sync
uv run alembic upgrade head
uv run python -m ingest.corpus
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
uv run python -m scripts.smoke_retrieval "Azure revenue growth" --ticker MSFT
```
