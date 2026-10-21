# Agent Instructions

This file is the source of truth for any coding agent (Claude Code, Cursor, Codex, etc.) working in this repo. Read it before touching code.

## Stack

- **Backend:** Python + FastAPI
- **Frontend:** Vite + React SPA + TypeScript
- **Database:** Supabase Postgres (users, chats, source documents, chunks)
- **Migrations:** SQLAlchemy models + Alembic from the backend
- **Retrieval:** `pgvector` + Postgres full-text search, fused with Reciprocal Rank Fusion
- **Auth:** Supabase Auth (email + password)
- **LLM + embeddings:** OpenAI
- **Hosting:** Railway (backend service + frontend service)

Stack is locked unless explicitly changed. Don't propose alternatives without a stated reason.

## Repo layout

```text
document-copilot/
├── AGENTS.md           # this file
├── README.md
├── data/               # local corpus + download script (payloads gitignored)
├── docs/               # specs, briefs, design notes
├── backend/            # FastAPI service (see backend/AGENTS.md)
└── frontend/           # React SPA (see frontend/AGENTS.md)
```

## Running modes

The backend supports two modes, controlled by `backend/.env`:

- **Real mode** — Supabase (auth + Postgres) and OpenAI keys are configured. This is the production path: Supabase Auth verifies JWTs, OpenAI powers embeddings, keyword extraction, the document agent, and the grounding judge.
- **Demo mode** — no keys configured (`DEMO_MODE=true` or keys left empty). Everything runs locally: Postgres via `DATABASE_URL`, local email auth with signed tokens, hashed bag-of-words embeddings, deterministic keyword extraction, an extractive demo agent, and substring-based grounding checks. Demo mode exists so the full pipeline (ingest → hybrid retrieval → grounded answers → citations) can be explored without external accounts.

Never silently switch modes. `app/config.py` decides once at startup and `GET /health` reports which mode is active.

## Dependency policy

**Default: write it yourself. Reach for a library only when the alternative would be non-trivial, error-prone, or reinvention of a standard.** Every dependency is a liability — bundle size, supply-chain risk, future upgrade work.

OK to depend on:

- Things that are genuinely hard to get right (HTTP clients, ASGI servers, SQL drivers, parsers, LLM SDKs, ORM, migrations, auth SDKs).
- The declared stack (FastAPI, React, Vite, Supabase clients, OpenAI SDK, etc.).

Not OK:

- Helper libraries that wrap 5–20 lines of stdlib or platform APIs.
- Frameworks where a function would do.
- "Nicer API" layers on top of an already-present dependency.

Before adding a runtime dep, answer in the commit message:

1. What exactly does it do that we can't write in <30 lines of clear code?
2. How often does it get used?
3. What's its maintenance / transitive-dep footprint?

Per-stack specifics live in `backend/AGENTS.md` and `frontend/AGENTS.md`.

## Configuration

A single settings module is the source of truth for environment per service (`backend/app/config.py`, `frontend/src/lib/env.ts`). Do not call `os.getenv` / read `process.env` directly in app code. Do not call `load_dotenv` anywhere. If a third-party SDK reads env vars directly, mirror them in the settings module — don't sprinkle `setdefault` elsewhere.

Fail fast on startup if required config is missing in real mode. In demo mode the defaults must work out of the box.

## Code style (universal)

- **Small, obvious functions.** A 15-line function with clear names beats a three-class abstraction.
- **No premature abstraction.** Three similar lines is better than a badly-named base class. Extract when there's a third caller, not a hypothetical one.
- **No error handling for cases that can't happen.** Trust internal callers and framework guarantees. Validate only at boundaries: HTTP input, external APIs, DB writes, untrusted parsing.
- **No backwards-compat shims** unless explicitly asked for.
- **No feature flags** added speculatively.
- **Comments:** explain *why* when non-obvious, never *what*. Remove stale TODOs.
- **Keep files focused.** Prefer small modules.

## Grounding contract (non-negotiable)

- Answers come only from retrieved passages. The turn registry is the citation allowlist.
- Every assistant answer carries at least one citation unless it explicitly reports insufficient evidence.
- Citations must reference chunks retrieved in the same turn, with verbatim excerpts.
- If grounding validation fails, return the controlled failure message — never an unverified answer.
