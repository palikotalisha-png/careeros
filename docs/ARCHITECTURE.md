# Architecture

```
        ┌─────────────────────────────┐
        │      Next.js (Vercel)        │
        │  App Router · Tailwind dark  │
        │  Clerk auth → Bearer JWT     │
        └──────────────┬──────────────┘
                       │ HTTPS (Bearer token)
                       ▼
        ┌─────────────────────────────┐
        │       FastAPI (Railway)      │
        │   routers → services → db    │
        └───┬─────────────────────┬────┘
            ▼                     ▼
   ┌────────────────┐   ┌────────────────────┐
   │  PostgreSQL    │   │  AIClient (OpenAI)  │
   │  SQLAlchemy 2  │   │  + mock fallback    │
   └────────────────┘   └────────────────────┘
            ▲
   ┌────────┴───────────────────────────┐
   │ files.py  PDF/DOCX parse + export   │
   │ ingest.py user-initiated URL fetch  │
   └─────────────────────────────────────┘
```

## Primary flow
`POST /api/analyze` is the orchestrator. Given a resume (uploaded or saved) and a job
description (pasted or fetched from a URL) it runs, in order:
1. `resume_ats.optimize` → recruiter analysis → XYZ rewrite → ATS scan → validation
2. `sponsorship.score_sponsorship` → score, probability, risk flags, compatibility
3. `matching.score_job` → overall match + explanation (personalized by learned prefs)
4. `company.research` → overview / BI / career intel / personalized insight
5. `interview.generate` → categorized questions with STAR frameworks

Each engine also has its own endpoint so the UI can re-run pieces independently.

## Backend module map
```
backend/app/
├── main.py        app + CORS + router registration
├── config.py      env settings (incl. Clerk + OpenAI)
├── database.py    engine/session/Base (Postgres or SQLite fallback)
├── deps.py        DB + auth (Clerk JWKS verify, dev-JWT fallback)
├── models.py      full SQLAlchemy schema
├── schemas.py     Pydantic request/response models
├── routers/       auth, profile, analyze, resume, cover_letter, company,
│                  interview, sponsorship, networking, tracker, dashboard, events
└── services/
    ├── ai.py          OpenAI wrapper + deterministic mock + prompt library
    ├── files.py       resume parse (PDF/DOCX) + export (PDF/DOCX)
    ├── ingest.py      URL → job-description text
    ├── resume_ats.py  recruiter analysis / XYZ rewrite / ATS scan / validation
    ├── sponsorship.py sponsorship scoring + risk-phrase detection
    ├── company.py      company research
    ├── interview.py    question generation + mock-interview feedback
    ├── networking.py   outreach message generation
    └── matching.py     overall match scoring + behavior-based personalization
```

## Learning loop
`POST /api/events` records view/save/click/apply/dismiss. `matching.update_preferences`
turns positive signals into a preference vector stored on the profile, which nudges future
match scores (`matching._personalize`).
