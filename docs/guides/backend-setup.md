# Backend Setup

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A Postgres the backend can reach (Supabase in real mode, local Postgres in demo mode) with the `pgvector` extension available.

## Steps

```bash
cd backend
cp .env.example .env     # edit DATABASE_URL (+ Supabase/OpenAI keys for real mode)
uv sync
uv run alembic upgrade head
```

Fetch and ingest the corpus (see `data/README.md`):

```bash
uv run ../data/download.py
uv run python -m ingest.corpus
```

Run the API:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health` reports `{"status":"ok","mode":"demo"|"real"}`.

## Demo mode

If Supabase/OpenAI keys are absent (or `DEMO_MODE=true`), the backend runs the keyless local path:

- auth: `POST /auth/demo/signin` and `/auth/demo/signup` issue locally-signed JWTs (any email; password must be ≥ 6 characters),
- embeddings: deterministic hashed bag-of-words vectors (same `vector(1536)` column),
- keywords: deterministic extraction (no LLM call),
- agent: `app/assistant/demo_agent.py` — extractive, quotes retrieved passages,
- grounding: verbatim substring checks instead of the LLM judge.

Demo mode is for exploring the pipeline. Switch to real mode for semantic search and LLM-generated answers, then re-run `python -m ingest.corpus` so chunks carry real embeddings.
