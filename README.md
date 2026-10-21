# Document Copilot

An internal AI chatbot that lets analysts ask questions about a corpus of SEC filings in plain English and get sourced, citable answers. Built end-to-end: React SPA → FastAPI → Postgres (`pgvector` + full-text search) → OpenAI.

> This project is a build-along of the **"Build a Full-Stack GenAI Project in 4 Hours"** workflow (FastAPI, React, Supabase). See `docs/` for the client brief and architecture.

## Screenshots

| | |
| --- | --- |
| ![Sign in](docs/final-1-login.png) | ![New chat](docs/final-2-home.png) |
| ![Streamed, cited answer](docs/final-4-answer.png) | ![Cited passage](docs/final-5-citation.png) |

*Sign in → new chat → streamed answer with citation chips → the cited passage (anchor chunk + neighbors, linked to EDGAR).*

## The client

**Driftwood Capital** — a (fictional) independent investment research firm. Their analysts spend half their week reading 10-Ks and 10-Qs before they can produce any original analysis. Document Copilot eats that intake work so they can skip straight to insight.

Full brief: [`docs/client-brief.md`](docs/client-brief.md)

## What it does

- **Grounded chat** — ask questions in plain English over 10-K filings (AAPL, MSFT, NVDA, AMZN, GOOGL; fiscal years 2021–2025). Every answer is generated from retrieved source passages.
- **Citations** — answers carry inline `[1]`, `[2]` markers and citation chips (company, form, filing date, page/section). Click a citation to open the source passage with surrounding chunks.
- **Grounding enforcement** — a fail-closed validator checks that every citation maps to a chunk retrieved in the same turn and that excerpts are verbatim. Unsupported answers are blocked, not polished.
- **Chat history** — threads are persisted per user; the sidebar lists, creates, and deletes threads.
- **Hybrid retrieval** — `pgvector` semantic search fused with Postgres full-text search using Reciprocal Rank Fusion, with neighbor-chunk hydration.
- **Pipeline transparency** — the UI streams live status (analyzing → searching → reading → verifying → streaming).

## Stack

| Layer | Choice |
| --- | --- |
| Backend | Python 3.12+ · FastAPI · PydanticAI (document agent) |
| Frontend | Vite · React SPA · TypeScript · Tailwind CSS · shadcn/ui · Vercel AI SDK |
| Database | Postgres (Supabase in production, local Postgres in demo mode) |
| Migrations | SQLAlchemy models + Alembic |
| Retrieval | `pgvector` + Postgres full-text search + RRF fusion |
| Auth | Supabase Auth (email) — or local demo auth in demo mode |
| LLM + embeddings | OpenAI (`gpt-4.1`, `text-embedding-3-small`) |
| Hosting | Railway |

## Repo layout

```text
document-copilot/
├── AGENTS.md           # agent instructions (read first)
├── README.md           # this file
├── data/               # local corpus + download script (payloads gitignored)
├── docs/
│   ├── client-brief.md # the client one-pager
│   ├── architecture.md # system design
│   └── guides/         # supabase / backend / frontend / railway setup
├── backend/            # FastAPI service (see backend/AGENTS.md)
└── frontend/           # React SPA (see frontend/AGENTS.md)
```

## Two ways to run it

### 1. Demo mode (zero external accounts)

The app ships with a demo mode that runs the entire pipeline — ingestion, hybrid retrieval, grounded answers, citations, chat history — against a local Postgres with no Supabase or OpenAI account:

- local email auth (any email + password ≥ 6 characters)
- hashed bag-of-words embeddings instead of OpenAI embeddings (retrieval leans on full-text search + RRF)
- an extractive demo agent instead of the LLM agent (it quotes retrieved passages and cites them verbatim)
- substring-based grounding checks instead of the LLM judge

```bash
# 1. Local Postgres with the pgvector extension available
createdb document_copilot

# 2. Backend
cd backend
cp .env.example .env            # defaults are demo-ready; point DATABASE_URL at your DB
uv sync                         # or: pip install -e ".[dev]"
uv run alembic upgrade head

# 3. Corpus (grabs the 5 most recent 10-Ks; raise FILINGS_PER_COMPANY for more)
uv run ../data/download.py
uv run python -m ingest.corpus

# 4. Serve
uv run uvicorn app.main:app --reload --port 8000

# 5. Frontend (separate terminal)
cd frontend
pnpm install
cp .env.example .env            # VITE_API_BASE_URL=/api (dev proxy)
pnpm dev
```

Sign in with any email and a password of 6+ characters. A "Demo mode" badge in the sidebar tells you it's not the production path.

### 2. Real mode (Supabase + OpenAI)

Follow [`docs/guides/supabase-setup.md`](docs/guides/supabase-setup.md), create an OpenAI API key, then fill `backend/.env`:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
DATABASE_URL=postgresql://postgres:...@db.your-project-ref.supabase.co:5432/postgres
OPENAI_API_KEY=sk-...
```

With keys present the backend automatically runs the production path: Supabase Auth verifies JWTs, OpenAI embeds queries and chunks, a PydanticAI agent (with `search_filings` / `read_chunk` / `read_chunks` / `read_surrounding_chunks` tools) produces the grounded answer, and an LLM judge validates citation support before anything streams to the browser. Re-run ingestion after switching so chunks carry real embeddings.

Deployment: [`docs/guides/railway-deployment.md`](docs/guides/railway-deployment.md).

## Ingestion pipeline

```bash
uv run ../data/download.py          # SEC EDGAR → data/downloads/<year>/*.htm + manifest.json
uv run python -m ingest.corpus      # manifest → source_documents → chunks → embeddings
```

`ingest.corpus` parses each filing's HTML, splits it into ~512-token chunks (sections tracked via `Item` headings, financial tables extracted row-group by row-group), embeds every chunk, and writes `document_chunks` with a generated `tsvector` for full-text search. Re-running is idempotent per filing.

## Scripts

```bash
uv run python -m scripts.smoke_retrieval "iPhone revenue Services 2024" --ticker AAPL
uv run python -m scripts.smoke_assistant "How does Apple describe Services growth?"
uv run pytest                       # unit tests (retrieval, fusion, grounding, chunking, chat)
```
