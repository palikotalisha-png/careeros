# Deployment

## Backend → Railway (or Render)
1. Create a Railway project; add a **PostgreSQL** plugin (sets `DATABASE_URL`).
2. New service from the `backend/` directory.
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set env vars (see below). Run `python -m app.seed` once from the Railway shell to load demo data.
5. (Render: use a Web Service, build `pip install -r requirements.txt`, same start command,
   add a managed Postgres instance.)

### Backend env vars
```
DATABASE_URL=postgresql+psycopg2://...        # provided by host
SECRET_KEY=<long-random-string>
FRONTEND_ORIGIN=https://your-app.vercel.app
OPENAI_API_KEY=sk-...                         # blank → mock AI
OPENAI_MODEL=gpt-4o-mini
CLERK_JWKS_URL=https://<app>.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://<app>.clerk.accounts.dev
```

## Frontend → Vercel
1. Import the repo, set root directory to `frontend/`.
2. Env vars:
```
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```
3. Deploy. Vercel auto-detects Next.js.

## Notes
- Configure CORS by setting `FRONTEND_ORIGIN` to your Vercel domain.
- Use Alembic for schema migrations in production instead of `create_all`.
- For background work (e.g. scheduled follow-up reminders) add a Railway cron service that
  hits an internal endpoint; the current scaffold keeps everything request-driven.
