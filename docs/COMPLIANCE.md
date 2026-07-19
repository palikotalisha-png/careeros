# Compliance notes

CareerOS does **not** scrape job boards — it never logs into or automates a session on
LinkedIn, Handshake, Interstride, Indeed, or Glassdoor. Job discovery only calls sources that
are public, documented, and either free or explicitly paid APIs. Data flows:

## 1. Daily job discovery (`app/jobs/adapters.py`, `app/services/discovery.py`)
A Vercel Cron job (`backend/vercel.json`, once/day) calls `POST /api/discovery/run`, which
runs whichever adapters are listed in `ENABLED_ADAPTERS`:

- **sample** — deterministic local demo jobs. No network call, always safe.
- **greenhouse** — the public [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html)
  (`boards-api.greenhouse.io`). No login, no key, no rate-limit-evasion. Only returns jobs for
  companies that already publish a public Greenhouse board.
- **lever** — the public [Lever Postings API](https://github.com/lever/postings-api)
  (`api.lever.co/v0/postings`). Same deal: public, documented, no auth.
- **google_jobs** — Google for Jobs results via [SerpApi](https://serpapi.com/google-jobs-api),
  a paid third-party API that returns Google's job-search results as structured JSON. This is
  not scraping Google directly; it's calling SerpApi's own API with your `SERPAPI_KEY`.
  Disabled (returns nothing) if no key is configured.

**LinkedIn, Handshake, Interstride, Indeed, and Glassdoor are intentionally not adapters.**
Automated collection from those sites requires either an authenticated user session or breaks
their Terms of Service (and in some cases anti-bot/CAPTCHA protections), which this app will
not do on a scheduled, unattended basis. Two things still cover those sources without
crossing that line:

- The **paste-a-job-URL** flow below (single, user-initiated fetch).
- The **browser extension**, which reads a job posting the user is already logged in and
  looking at themselves — it acts on the user's own session, not an automated crawler.

## 2. Job-description URL fetch
When a user pastes a posting URL, `services/ingest.py` performs a **single, user-initiated**
HTTPS GET and extracts visible text. This is a per-request convenience, not bulk crawling.
For boards that block direct fetches (LinkedIn, Indeed, etc.), the UI prompts the user to
paste the description text instead. Do not turn this into a scheduled crawler.

## 3. Public sponsorship data
Sponsorship intelligence is built only from **public, redistributable** datasets, loaded into
the `companies` and `sponsorship_records` tables:

- **H-1B** — U.S. DOL OFLC LCA disclosure files
- **E-Verify** — USCIS E-Verify employer list
- **PERM / Green card** — DOL PERM disclosure data

`services/sponsorship.py` joins on a normalized company name to compute the sponsorship score,
probability, and International Student Compatibility Score, and runs regex risk-phrase
detection on the job description (citizen-only, clearance, "no sponsorship", etc.).

## AI
All LLM calls go through `services/ai.py`. No user data is sent anywhere unless `OPENAI_API_KEY`
is set; the mock provider runs fully offline.
