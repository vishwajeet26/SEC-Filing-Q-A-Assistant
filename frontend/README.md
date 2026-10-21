# Document Copilot — Frontend

Vite + React SPA (TypeScript, Tailwind CSS, shadcn/ui, Vercel AI SDK). See `AGENTS.md` for the rules and the root README for the full setup.

## Quick start

```bash
cp .env.example .env
pnpm install
pnpm dev          # http://localhost:5173
```

The dev server proxies `/api` to `http://127.0.0.1:8000`. Leave the Supabase variables empty to use the backend's demo auth; fill them for Supabase email auth.
