"""Pull a job description from a pasted URL (compliant: single user-initiated fetch)."""
from __future__ import annotations
import re
import httpx


def fetch_job_description(url: str) -> dict:
    """Best-effort fetch + text extraction. Returns {title, company, description}."""
    try:
        r = httpx.get(url, timeout=15, follow_redirects=True,
                      headers={"User-Agent": "Mozilla/5.0 CareerOS"})
        html = r.text
    except Exception as e:
        return {"title": "", "company": "", "description": "", "error": str(e)}

    title = _meta(html, "og:title") or _tag(html, "title")
    company = _meta(html, "og:site_name")
    text = _strip_html(html)
    return {"title": title, "company": company, "description": text[:8000], "url": url}


def _meta(html: str, prop: str) -> str:
    m = re.search(rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)',
                  html, re.I)
    return m.group(1).strip() if m else ""


def _tag(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def _strip_html(html: str) -> str:
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()
