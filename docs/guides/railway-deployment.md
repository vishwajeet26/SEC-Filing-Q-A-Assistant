# Railway Deployment

Two services, one hosted Postgres (Supabase).

## Backend service

- **Root directory:** `backend`
- **Start command:** the Dockerfile builds a uv-managed image (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
- **Variables:** everything from `backend/.env.example` — Supabase keys, `DATABASE_URL` (direct connection), `OPENAI_API_KEY`, and `ALLOWED_ORIGINS` set to your frontend Railway domain.

## Frontend service

- **Root directory:** `frontend`
- **Build:** the Dockerfile builds the Vite app and serves it with Caddy.
- **Variables:** `VITE_API_BASE_URL=https://<backend>.up.railway.app/api`, plus the Supabase URL/anon key (or leave them empty to keep demo auth).

## Checklist before going live

1. `alembic upgrade head` has been run against the Supabase direct URL.
2. Corpus ingested with real OpenAI embeddings (`python -m ingest.corpus`).
3. `ALLOWED_ORIGINS` contains the exact frontend origin(s).
4. Email confirmation policy in Supabase matches your user onboarding plan.
