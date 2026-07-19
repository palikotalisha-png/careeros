"""Daily job discovery: pulls from enabled adapters, dedupes, saves, and notifies users.

Triggered by a Vercel Cron hitting POST /api/discovery/run once a day (see backend/vercel.json)
or manually for testing. See docs/COMPLIANCE.md for what each source is and isn't allowed to do.
"""
from __future__ import annotations
import hashlib
import re
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.config import settings
from app.jobs.adapters import SampleAdapter, GreenhouseAdapter, LeverAdapter, GoogleJobsAdapter

# Starter list of companies with long-standing public Greenhouse job boards, so the feed isn't
# empty on day one. ATS providers change over time — if a token is stale the adapter just
# returns zero jobs for it, nothing breaks. Add real targets by favoriting a company in the
# app (Jobs page) or by adding applications for it; discovery automatically tries those too.
STARTER_GREENHOUSE = ["airbnb", "stripe", "doordash", "coinbase", "robinhood", "asana", "pinterest"]
STARTER_GOOGLE_QUERIES = [
    "new grad software engineer visa sponsorship",
    "data analyst entry level sponsorship",
]


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def _dedup_hash(title: str, company: str, location: str) -> str:
    key = f"{title.strip().lower()}|{company.strip().lower()}|{location.strip().lower()}"
    return hashlib.sha256(key.encode()).hexdigest()


def _target_companies(db: Session) -> list[str]:
    slugs = {s for s in STARTER_GREENHOUSE}
    for (name,) in db.query(models.FavoriteCompany.company_name).distinct():
        if name:
            slugs.add(_slug(name))
    for (name,) in db.query(models.Application.company).distinct():
        if name:
            slugs.add(_slug(name))
    return sorted(s for s in slugs if s)


def _google_queries(db: Session) -> list[str]:
    if not settings.serpapi_key:
        return []
    queries = set(STARTER_GOOGLE_QUERIES)
    for p in db.query(models.Profile).limit(25):
        loc = (p.preferred_locations or [""])[0] if p.preferred_locations else ""
        if p.major:
            q = f"{p.major} jobs" + (f" {loc}" if loc else "")
            queries.add(q.strip())
    return list(queries)[:8]


def run(db: Session) -> dict:
    enabled = set(settings.adapters)
    raw: list[dict] = []

    if "sample" in enabled:
        raw += SampleAdapter().fetch()
    if "greenhouse" in enabled:
        raw += GreenhouseAdapter(_target_companies(db)).fetch()
    if "lever" in enabled:
        raw += LeverAdapter(_target_companies(db)).fetch()
    if "google_jobs" in enabled:
        raw += GoogleJobsAdapter(_google_queries(db)).fetch()

    created = 0
    seen_hashes: set[str] = set()
    for j in raw:
        if not j.get("title") or not j.get("company_name"):
            continue
        h = _dedup_hash(j["title"], j["company_name"], j.get("location", ""))
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        if db.query(models.Job).filter_by(dedup_hash=h).first():
            continue

        dp = None
        raw_date = j.get("date_posted") or ""
        if raw_date:
            try:
                dp = datetime.fromisoformat(raw_date[:10]).date()
            except Exception:
                dp = None

        company = _get_or_create_company(db, j["company_name"])
        job = models.Job(
            company_id=company.id if company else None,
            title=j["title"][:300],
            company_name=j["company_name"][:200],
            location=(j.get("location") or "")[:200],
            description=j.get("description", ""),
            salary=(j.get("salary") or "")[:100],
            source=j.get("source", ""),
            apply_url=j.get("apply_url", ""),
            date_posted=dp,
            e_verify=company.e_verify if company else None,
            dedup_hash=h,
        )
        db.add(job)
        created += 1

    db.commit()
    if created:
        _notify_new(db, created)
    return {"fetched": len(raw), "new_jobs": created, "sources": sorted(enabled)}


def _get_or_create_company(db: Session, name: str) -> models.Company | None:
    if not name:
        return None
    norm = _slug(name)
    company = db.query(models.Company).filter_by(normalized_name=norm).first()
    if not company:
        company = models.Company(name=name, normalized_name=norm)
        db.add(company); db.commit(); db.refresh(company)
    return company


def _notify_new(db: Session, created: int) -> None:
    label = f"{created} new job{'s' if created != 1 else ''} found today"
    for (user_id,) in db.query(models.User.id).all():
        db.add(models.Notification(
            user_id=user_id, kind="new_jobs", title=label,
            body="Check the Jobs feed for today's new openings.", link="/jobs",
        ))
    db.commit()
