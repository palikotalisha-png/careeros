# CareerOS — AI Job-Application Copilot for International Students

CareerOS helps international students and recent graduates turn a single job posting into a
complete, optimized application. You **paste a job description or URL and upload your resume**;
CareerOS analyzes the fit and generates everything you need to apply with confidence.

It acts like a personal recruiter, ATS expert, interview coach, company researcher, and career
advisor — built specifically for people who need work sponsorship.

> **Status:** Runnable reference application. The data model, API, AI service layer, file
> processing (PDF/DOCX in and out), sample data, and a premium Next.js UI are implemented.
> Without an `OPENAI_API_KEY` the backend runs a **deterministic mock AI** so every feature
> works offline; add a key to switch to live OpenAI generation. This is a clean, honest
> foundation engineered to extend — not a finished commercial product.

## What it does

The primary flow: **upload resume → paste job description or URL → analyze → save to tracker.**

| # | Feature | What you get |
|---|---------|--------------|
| 1 | Resume Analyzer | Recruiter-style match score, top-5 missing keywords, top-3 red flags, strengths, gaps, recommendations |
| 2 | ATS Resume Optimizer | Experience rewritten with the Google **XYZ** formula — strong verbs, measurable outcomes, keywords woven in, nothing fabricated |
| 3 | ATS + Hiring-Manager Review | Skipped sections, weak bullets, still-missing keywords, before/after, ATS + recruiter scores |
| 4 | ATS Validation | No tables/graphics/text-boxes/icons, standard fonts, reverse-chronological → compliance score + clean PDF/DOCX |
| 5 | Cover Letter Generator | Human-sounding, personalized, editable; export PDF/DOCX |
| 6 | Company Research Engine | Overview, business intelligence, career intelligence, "why this is a fit for you" |
| 7 | Interview Intelligence | Behavioral / technical / role / company questions, each with why-asked, strong-answer notes, STAR framework + sample; mock-interview practice with feedback |
| 8 | Sponsorship Analysis | OPT / STEM-OPT friendliness, sponsorship likelihood, E-Verify, **risk-phrase detection** (citizen-only, clearance, no sponsorship), International Student Compatibility Score |
| 9 | Networking Assistant | LinkedIn / referral / recruiter / thank-you / follow-up messages, personalized |
| 10 | Application Tracker | Company, title, URL, dates, status, notes, interview & follow-up dates |
| 11 | Dashboard | Active apps, apps this month, interviews, offers, ATS-score improvements, upcoming interviews & follow-ups |

## Stack

Next.js (App Router) · React · Tailwind CSS (dark mode) · FastAPI · SQLAlchemy 2 · PostgreSQL ·
Clerk auth (with dev-credential fallback) · OpenAI API (mock fallback) · PDF + DOCX processing ·
Vercel (web) + Railway (api + db).

## Quick start

```bash
# Backend
cd backend
cp .env.example .env                 # works as-is with mock AI + dev auth
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# For a zero-infra local run, use SQLite:
export DATABASE_URL="sqlite:////tmp/careeros.db"
python -m app.seed                   # demo@careeros.app / demo1234
uvicorn app.main:app --reload        # http://localhost:8000/docs

# Frontend
cd ../frontend
cp .env.example .env.local
npm install
npm run dev                          # http://localhost:3000
```

## Docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design & module map
- [`docs/DATABASE.md`](docs/DATABASE.md) — schema & tables
- [`docs/API.md`](docs/API.md) — endpoint reference
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — Vercel + Railway
- [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) — URL fetching & public sponsorship data

## Repo layout

```
CareerOS/
├── backend/    FastAPI app, models, routers, services, seed
├── frontend/   Next.js + Tailwind UI (dark mode, mobile-friendly)
└── docs/       Architecture, DB, API, deployment, compliance
```
