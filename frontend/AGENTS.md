# Frontend Agent Instructions

Read the root `AGENTS.md` first. This file covers frontend-specific rules.

## Layout

```text
src/
├── components/
│   ├── chat/          # product components (layout, messages, citations, sheet)
│   └── ui/            # shadcn/ui primitives — hand-rolled, no CLI
├── contexts/          # thread list context
├── hooks/             # session, threads, chat transport
├── lib/               # env, supabase/demo auth, http, api, chat, citations
├── pages/             # route-level screens
├── App.tsx            # routing only
└── main.tsx           # mount + Toaster
```

## Rules

- **The browser stays thin.** No retrieval logic, no OpenAI calls, no direct DB access, no service credentials. It renders chat state and streams from FastAPI.
- **Env access** goes through `src/lib/env.ts` only. `VITE_API_BASE_URL` may be empty-ish (`/api`) for same-origin deployments.
- **Auth client**: `src/lib/supabase.ts` returns either the real Supabase client or the demo auth shim with the same consumed surface. Product code never branches on which one is active (only the login hint and sidebar badge do).
- **Streaming protocol**: Vercel AI SDK v5 (`useChat` + `DefaultChatTransport`). The transport customizes `prepareSendMessagesRequest` to send `{ threadId, messages }` and tee's the response to observe `data-status` parts for the pipeline indicator.
- **Citations** are data parts (`data-citation`) on assistant messages; `[n]` markers in text render as buttons via `AssistantMarkdown`. Unknown data parts must be ignored gracefully.
- **Styling**: Tailwind v4, strict light-only monochrome theme in `index.css`. shadcn/ui primitives live in `components/ui/` and are edited in place.
- **No new heavy deps** for things a few lines of code solve (see root dependency policy).

## Commands

```bash
pnpm install
pnpm dev        # http://localhost:5173 (proxies /api → 127.0.0.1:8000)
pnpm build      # tsc -b && vite build
```
