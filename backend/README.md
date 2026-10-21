# Document Copilot — Backend

FastAPI service: auth, chat orchestration, hybrid retrieval, grounding, persistence. See `AGENTS.md` for the rules and the root README for the full setup.

## Quick start (demo mode)

```bash
cp .env.example .env          # defaults point at a local Postgres
uv sync
uv run alembic upgrade head
uv run ../data/download.py    # fetch the corpus
uv run python -m ingest.corpus
uv run uvicorn app.main:app --reload --port 8000
```

`GET /api/health` → `{"status":"ok","mode":"demo"}`.

Switch to real mode by filling `SUPABASE_*`, `DATABASE_URL`, and `OPENAI_API_KEY` in `.env`, then re-run `python -m ingest.corpus` so chunks carry real embeddings.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | liveness + mode |
| GET | `/api/auth/me` | current user ( bearer token) |
| POST | `/api/auth/demo/signin` | demo-mode session (email + password ≥ 6 chars) |
| GET | `/api/chat/threads` | list threads for the user |
| POST | `/api/chat/threads` | create a thread |
| DELETE | `/api/chat/threads/{id}` | delete a thread |
| GET | `/api/chat/threads/{id}/messages` | message history with citations |
| GET | `/api/chat/citations/{chunk_id}/context` | anchor + neighbor chunks, table context |
| POST | `/api/chat/stream` | one chat turn; AI-SDK-compatible SSE stream |
