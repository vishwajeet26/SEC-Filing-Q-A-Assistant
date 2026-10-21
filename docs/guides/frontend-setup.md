# Frontend Setup

## Prerequisites

- Node.js 20+ (LTS)
- pnpm (`corepack enable && corepack prepare pnpm@latest --activate`)

## Steps

```bash
cd frontend
cp .env.example .env
pnpm install
pnpm dev          # http://localhost:5173
```

## Environment

| Variable | Meaning |
| --- | --- |
| `VITE_API_BASE_URL` | Backend base. `/api` in dev (proxied by Vite to `http://127.0.0.1:8000`); the full backend URL in production. |
| `VITE_SUPABASE_URL` | Supabase project URL. **Leave empty for demo auth.** |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key. **Leave empty for demo auth.** |

When the Supabase variables are empty the app uses the local demo auth client (`src/lib/demo-auth.ts`) which mirrors the small `supabase.auth` surface the app consumes.
