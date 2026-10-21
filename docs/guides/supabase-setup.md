# Supabase Setup

Supabase provides auth and the hosted Postgres used in real mode.

1. **Create an account** at [supabase.com](https://supabase.com) (free tier is fine).
2. **Create a project** — remember the database password you choose.
3. **Collect credentials** from *Project Settings → API*:
   - `SUPABASE_URL` — the project URL.
   - `SUPABASE_ANON_KEY` — the anon public key.
   - `SUPABASE_SERVICE_ROLE_KEY` — the service role key (backend only, never in the browser).
4. **Collect the database URL** from *Project Settings → Database → Connection string*:
   - Use the **direct** connection (`db.<ref>.supabase.co:5432`) for Alembic and the backend. Do **not** use the transaction pooler URL — migrations and `pgvector`/index DDL require a session connection.
   - URL-encode special characters in the password.
5. Put everything in `backend/.env` (see `backend/.env.example`), then run migrations:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```
6. **Auth**: the project's email/password provider is enabled by default. For testing, disable email confirmation under *Authentication → Providers → Email* or confirm test addresses from the inbox.

## Notes

- RLS: this backend accesses Postgres over a direct connection with full privileges (equivalent to the service role). Table ownership stays with the backend; the anon key is only used for verifying user tokens.
- Keep the service role key out of the frontend at all times.
