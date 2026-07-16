"""Visa & sponsorship intelligence: scores, probabilities, risk flags."""
from __future__ import annotations
import re
from sqlalchemy.orm import Session
from app import models

RISK_PATTERNS = {
    "U.S. Citizen Required": r"u\.?s\.? citizen(ship)? (required|only)",
    "Security Clearance Required": r"(security )?clearance",
    "Sponsorship Not Available": r"(no|not) (provide|offer|able).{0,20}sponsor|sponsorship not",
    "Permanent Work Authorization Required": r"permanent work authorization|green card required",
    "U.S. Persons Only": r"u\.?s\.? persons? only|itar",
}


def detect_risk_flags(text: str) -> list[str]:
    t = (text or "").lower()
    return [label for label, pat in RISK_PATTERNS.items() if re.search(pat, t)]


def score_sponsorship(company_name: str, job: models.Job | None,
                      user: models.User | None, db: Session | None = None) -> dict:
    flags = detect_risk_flags(job.description if job else "")
    # Base from public records if we have them, else AI/mock estimate.
    h1b_history: list = []
    base = 50
    e_verify = job.e_verify if job else None

    if db is not None:
        norm = _norm(company_name)
        company = (
            db.query(models.Company)
            .filter(models.Company.normalized_name == norm)
            .first()
        )
        if company:
            e_verify = company.e_verify if company.e_verify is not None else e_verify
            recs = [r for r in company.sponsorship_records if r.record_type == "h1b"]
            h1b_history = [
                {"fiscal_year": r.fiscal_year, "count": r.count, "title": r.job_title}
                for r in recs
            ]
            total = sum(r.count for r in recs)
            base = min(95, 40 + total)  # more petitions → higher score

    if e_verify:
        base += 10
    if flags:
        base = min(base, 15)  # hard blockers dominate

    score = max(0, min(100, base))
    prob = "High" if score >= 70 else "Medium" if score >= 45 else "Low"

    intl = score
    if user and user.profile:
        if user.profile.stem_opt_eligible:
            intl = min(100, intl + 5)
    intl = max(0, min(100, intl - (20 if flags else 0)))

    return {
        "sponsorship_score": score,
        "sponsorship_probability": prob,
        "intl_compat_score": intl,
        "e_verify": e_verify,
        "h1b_history": h1b_history,
        "risk_flags": flags,
        "summary": _summary(score, prob, flags, e_verify, h1b_history),
    }


def _summary(score, prob, flags, e_verify, h1b):
    if flags:
        return "Warning: " + "; ".join(flags) + ". Likely not viable for sponsorship."
    bits = [f"Sponsorship probability {prob} ({score}/100)."]
    if e_verify:
        bits.append("Employer is in E-Verify.")
    if h1b:
        bits.append(f"{sum(h.get('count',0) for h in h1b)} recent H-1B petitions on record.")
    return " ".join(bits)


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())
