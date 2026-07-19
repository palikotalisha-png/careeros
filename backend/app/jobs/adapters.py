"""Job source adapters — each returns a flat list of raw job dicts.

Compliance: every adapter here calls a **public, documented JSON API** (Greenhouse, Lever,
SerpApi's Google Jobs endpoint) or generates local sample data. None of them log into or
scrape LinkedIn, Handshake, Interstride, Indeed, or Glassdoor — those platforms require an
authenticated session and/or prohibit automated collection in their Terms of Service. See
docs/COMPLIANCE.md for the full policy and for how those sources are still supported (via the
user-initiated "paste a job URL" flow and the browser extension, both of which act on the
user's own, already-logged-in session rather than a scheduled crawler).
"""
from __future__ import annotations
import re
from datetime import date, datetime
import httpx
from app.config import settings

TIMEOUT = 15


def _clean(html_or_text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html_or_text or "")
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class Adapter:
    id = "base"

    def fetch(self) -> list[dict]:
        raise NotImplementedError


class SampleAdapter(Adapter):
    """Deterministic demo jobs so the feed and matching pipeline work with zero external
    config. Always enabled by default (ENABLED_ADAPTERS=sample)."""
    id = "sample"

    def fetch(self) -> list[dict]:
        today = date.today().isoformat()
        rows = [
            ("Data Analyst", "Northwind Analytics", "Remote",
             "Analyze product data, build dashboards, partner with the growth team. "
             "SQL, Python, and Tableau required. Northwind is an E-Verify employer and has "
             "sponsored H-1B visas for analytics hires in the past.",
             "$75,000-$95,000"),
            ("Software Engineer, New Grad", "Fernwood Systems", "New York, NY",
             "Join our platform team building distributed systems in Python and Go. "
             "We welcome new graduates including F-1/OPT candidates; we sponsor H-1B.",
             "$110,000-$130,000"),
            ("Machine Learning Engineer", "Cobalt Health", "Boston, MA",
             "Build ML pipelines for clinical data. Must be a U.S. citizen or permanent "
             "resident due to federal contract requirements. Security clearance required.",
             ""),
            ("Business Analyst", "Harbor Retail Group", "Chicago, IL",
             "Support merchandising analytics. Excel, SQL. No sponsorship available for "
             "this role at this time.",
             "$65,000-$78,000"),
            ("Cloud Support Engineer", "Meridian Cloud", "Austin, TX",
             "Troubleshoot customer cloud deployments (AWS, Kubernetes). Meridian is "
             "E-Verify participant and sponsors STEM OPT / H-1B for technical roles.",
             "$85,000-$105,000"),
            ("Product Analyst Intern", "Lighthouse Media", "Remote",
             "Summer internship supporting the product analytics team. CPT-eligible.",
             "$32/hr"),
        ]
        out = []
        for title, company, loc, desc, salary in rows:
            out.append({
                "title": title, "company_name": company, "location": loc,
                "description": desc, "salary": salary,
                "apply_url": f"https://example.com/jobs/{re.sub(r'[^a-z0-9]+', '-', title.lower())}",
                "date_posted": today, "source": self.id,
            })
        return out


class GreenhouseAdapter(Adapter):
    """Public Greenhouse Job Board API — https://developers.greenhouse.io/job-board.html
    No auth, no scraping: `GET boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`.
    """
    id = "greenhouse"

    def __init__(self, tokens: list[str]):
        self.tokens = tokens

    def fetch(self) -> list[dict]:
        out = []
        for token in self.tokens:
            try:
                r = httpx.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
                    params={"content": "true"}, timeout=TIMEOUT,
                )
                if r.status_code != 200:
                    continue
                data = r.json()
            except Exception:
                continue
            for j in data.get("jobs", []):
                loc = (j.get("location") or {}).get("name", "")
                out.append({
                    "title": j.get("title", ""),
                    "company_name": token.replace("-", " ").title(),
                    "location": loc,
                    "description": _clean(j.get("content", "")),
                    "salary": "",
                    "apply_url": j.get("absolute_url", ""),
                    "date_posted": (j.get("updated_at") or "")[:10],
                    "source": self.id,
                })
        return out


class LeverAdapter(Adapter):
    """Public Lever Postings API — https://github.com/lever/postings-api
    `GET api.lever.co/v0/postings/{token}?mode=json`.
    """
    id = "lever"

    def __init__(self, tokens: list[str]):
        self.tokens = tokens

    def fetch(self) -> list[dict]:
        out = []
        for token in self.tokens:
            try:
                r = httpx.get(
                    f"https://api.lever.co/v0/postings/{token}",
                    params={"mode": "json"}, timeout=TIMEOUT,
                )
                if r.status_code != 200:
                    continue
                data = r.json()
            except Exception:
                continue
            for j in data:
                cat = j.get("categories", {}) or {}
                created = j.get("createdAt")
                dp = ""
                if created:
                    try:
                        dp = datetime.utcfromtimestamp(created / 1000).date().isoformat()
                    except Exception:
                        dp = ""
                out.append({
                    "title": j.get("text", ""),
                    "company_name": token.replace("-", " ").title(),
                    "location": cat.get("location", ""),
                    "description": _clean(j.get("descriptionPlain") or j.get("description", "")),
                    "salary": "",
                    "apply_url": j.get("hostedUrl", ""),
                    "date_posted": dp,
                    "source": self.id,
                })
        return out


class GoogleJobsAdapter(Adapter):
    """Google for Jobs results via SerpApi (https://serpapi.com/google-jobs-api) — a paid,
    documented third-party API. This is NOT scraping Google directly. Requires SERPAPI_KEY;
    returns nothing if unset (no silent fake data)."""
    id = "google_jobs"

    def __init__(self, queries: list[str]):
        self.queries = queries

    def fetch(self) -> list[dict]:
        if not settings.serpapi_key:
            return []
        out = []
        for q in self.queries:
            try:
                r = httpx.get(
                    "https://serpapi.com/search.json",
                    params={"engine": "google_jobs", "q": q, "api_key": settings.serpapi_key},
                    timeout=20,
                )
                data = r.json()
            except Exception:
                continue
            for j in data.get("jobs_results", []):
                links = j.get("related_links") or j.get("apply_options") or []
                apply_url = ""
                if links and isinstance(links, list):
                    apply_url = links[0].get("link", "")
                out.append({
                    "title": j.get("title", ""),
                    "company_name": j.get("company_name", ""),
                    "location": j.get("location", ""),
                    "description": (j.get("description", "") or "")[:6000],
                    "salary": (j.get("detected_extensions") or {}).get("salary", ""),
                    "apply_url": apply_url or j.get("share_link", ""),
                    "date_posted": "",
                    "source": self.id,
                })
        return out


ADAPTER_CLASSES = {
    "sample": SampleAdapter,
    "greenhouse": GreenhouseAdapter,
    "lever": LeverAdapter,
    "google_jobs": GoogleJobsAdapter,
}
