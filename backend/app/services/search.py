"""Thin wrapper around a web-search API (SerpApi) for pulling real, citable public results —
e.g. candidate-reported interview questions from Reddit/Glassdoor/Indeed/Blind threads.

No API key configured -> returns [] so callers can fall back to an honest "connect a key"
placeholder instead of fabricating sources.
"""
from __future__ import annotations
import httpx
from app.config import settings

SOURCE_DOMAINS = ["reddit.com", "glassdoor.com", "indeed.com", "teamblind.com",
                   "levels.fyi", "geeksforgeeks.org", "1point3acres.com"]


def enabled() -> bool:
    return bool(settings.serpapi_key)


def search(query: str, num: int = 10) -> list[dict]:
    """Return [{title, link, snippet, domain}] from SerpApi's Google engine. [] if disabled
    or the request fails — callers must treat that as 'no live data', not an error."""
    if not enabled():
        return []
    try:
        r = httpx.get(
            "https://serpapi.com/search",
            params={"engine": "google", "q": query, "num": num, "api_key": settings.serpapi_key},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    out = []
    for item in data.get("organic_results", []):
        link = item.get("link", "")
        domain = link.split("/")[2] if "//" in link else link
        out.append({
            "title": item.get("title", ""),
            "link": link,
            "snippet": item.get("snippet", ""),
            "domain": domain,
        })
    return out


def search_reported_questions(company: str, role: str, num: int = 10) -> list[dict]:
    """Search public forums/review sites for candidate-reported interview questions."""
    site_filter = " OR ".join(f"site:{d}" for d in SOURCE_DOMAINS)
    query = f'{company} {role} interview questions ({site_filter})'
    results = search(query, num=num)
    if not results:
        # Fall back to an unfiltered query in case the site: filter over-constrains.
        results = search(f"{company} {role} interview questions candidate experience", num=num)
    return results
