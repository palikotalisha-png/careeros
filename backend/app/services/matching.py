"""AI job-match scoring + a learning loop that re-ranks from user behavior."""
from __future__ import annotations
from collections import Counter
from app import models
from app.services.ai import ai
from app.services.sponsorship import score_sponsorship


def score_job(user: models.User, job: models.Job) -> dict:
    p = user.profile
    resume = (p.resume_text if p else "") or ""
    skills = ", ".join(p.skills) if p and p.skills else ""
    grad = p.graduation_date.isoformat() if p and p.graduation_date else "unknown"
    goals = p.career_goals if p else ""

    prompt = (
        f"Analyze this job for an international student.\n"
        f"RESUME:\n{resume}\nSKILLS: {skills}\nGRADUATION: {grad}\nGOALS: {goals}\n"
        f"REQUIRES SPONSORSHIP: {p.requires_sponsorship if p else True}\n\n"
        f"JOB: {job.title} at {job.company_name} ({job.location})\n{job.description}"
    )
    res = ai.json(
        "You are a career match engine for international students. "
        "Return JSON with match_score, missing_keywords, red_flags, "
        "matching_qualifications, experience_gaps, recommendations.",
        prompt,
        seed_key=f"match:{user.id}:{job.id}",
    )

    spons = score_sponsorship(job.company_name, job, user)
    match_score = int(res.get("match_score", 0))
    match_score = _personalize(p, job, match_score)

    return {
        "match_score": match_score,
        "sponsorship_score": spons["sponsorship_score"],
        "sponsorship_probability": spons["sponsorship_probability"],
        "intl_compat_score": spons["intl_compat_score"],
        "strengths": res.get("matching_qualifications", []),
        "risks": res.get("red_flags", []),
        "missing_skills": res.get("missing_keywords", []),
        "missing_qualifications": res.get("experience_gaps", []),
        "recommended_actions": res.get("recommendations", []),
        "risk_flags": spons["risk_flags"],
        "explanation": _explain(match_score, spons, res),
    }


def _personalize(profile: models.Profile | None, job: models.Job, score: int) -> int:
    """Nudge score using the learned preference vector (industries/locations clicked)."""
    if not profile or not profile.preference_vector:
        return score
    pv = profile.preference_vector
    bonus = 0
    for token, weight in pv.items():
        if token.lower() in (job.title + " " + job.location + " " + job.company_name).lower():
            bonus += min(int(weight), 5)
    return max(0, min(100, score + min(bonus, 10)))


def _explain(match: int, spons: dict, res: dict) -> str:
    parts = [f"Match {match}/100."]
    if res.get("matching_qualifications"):
        parts.append("Strengths: " + ", ".join(res["matching_qualifications"][:2]) + ".")
    if res.get("experience_gaps"):
        parts.append("Gaps: " + ", ".join(res["experience_gaps"][:2]) + ".")
    parts.append(
        f"Sponsorship {spons['sponsorship_probability'].lower()} "
        f"({spons['sponsorship_score']}/100) based on H-1B/E-Verify signals."
    )
    return " ".join(parts)


def update_preferences(profile: models.Profile, events: list[models.UserEvent],
                       jobs_by_id: dict[str, models.Job]) -> dict:
    """Build a simple preference vector from positive signals (save/click/apply)."""
    weights = {"save": 2, "click": 1, "apply": 3, "dismiss": -2, "view": 0}
    counter: Counter = Counter()
    for e in events:
        job = jobs_by_id.get(e.job_id or "")
        if not job:
            continue
        w = weights.get(e.event_type, 0)
        if w == 0:
            continue
        for token in [job.company_name] + job.location.split(","):
            t = token.strip()
            if t:
                counter[t] += w
    return {k: v for k, v in counter.items() if v > 0}
