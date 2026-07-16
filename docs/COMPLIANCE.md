# Compliance notes

CareerOS does **not** scrape job boards. Two data flows touch external/public data:

## 1. Job-description URL fetch
When a user pastes a posting URL, `services/ingest.py` performs a **single, user-initiated**
HTTPS GET and extracts visible text. This is a per-request convenience, not bulk crawling.
For boards that block direct fetches (LinkedIn, Indeed, etc.), the UI prompts the user to
paste the description text instead. Do not turn this into a scheduled crawler.

## 2. Public sponsorship data
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
