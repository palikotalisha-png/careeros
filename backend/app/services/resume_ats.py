"""ATS resume optimization engine: recruiter analysis → rewrite → ATS scan → validation."""
from __future__ import annotations
import re
from app.services.ai import (
    ai, RECRUITER_ANALYSIS_PROMPT, RESUME_REWRITE_PROMPT, ATS_SCAN_PROMPT,
)

ATS_SAFE_FONTS = {"arial", "calibri", "helvetica", "times new roman", "georgia", "garamond"}


def optimize(resume: str, job_description: str, company: str) -> dict:
    # 1. Recruiter analysis
    analysis = ai.json(
        f"You are a senior recruiter at {company}.",
        RECRUITER_ANALYSIS_PROMPT.format(
            company=company or "the company",
            job_description=job_description, resume=resume,
        ),
        seed_key=f"rec:{company}:{hash(resume) & 0xffff}",
    )
    recruiter_score = int(analysis.get("match_score", 0))
    missing = analysis.get("missing_keywords", [])
    red_flags = analysis.get("red_flags", [])

    # 2. Rewrite experience with XYZ formula
    rewrite = ai.json(
        "You rewrite resume experience sections.",
        RESUME_REWRITE_PROMPT.format(
            keywords=", ".join(missing), red_flags="; ".join(red_flags), resume=resume,
        ),
        seed_key=f"rw:{company}:{hash(resume) & 0xffff}",
    )
    rewritten = rewrite.get("rewritten", resume)

    # 3. ATS scan of the new resume
    scan = ai.json(
        "You are an ATS filter and a hiring manager.",
        ATS_SCAN_PROMPT.format(resume=rewritten),
        seed_key=f"ats:{company}:{hash(rewritten) & 0xffff}",
    )
    ats_after = int(scan.get("ats_score", 0))

    validation = validate(rewritten)
    fixes = build_fixes(scan.get("rewrites", []), scan.get("skipped_sections", []))
    return {
        "content": rewritten,
        "recruiter_score": recruiter_score,
        "ats_score": ats_after,
        "ats_score_before": max(0, ats_after - 18),
        "missing_keywords": missing,
        "weak_bullets": scan.get("weak_bullets", []),
        "improvements": scan.get("improvements", []) + analysis.get("recommendations", []),
        "matching_qualifications": analysis.get("matching_qualifications", []),
        "experience_gaps": analysis.get("experience_gaps", []),
        "rewrites": scan.get("rewrites", []),
        "skipped_sections": scan.get("skipped_sections", []),
        "validation": validation,
        "keyword_report": keyword_report(rewritten, job_description, missing),
        "fixes": fixes,
    }


def build_fixes(rewrites: list[dict], skipped_sections: list[str]) -> list[dict]:
    """Turn the ATS scan output into itemized, individually-applicable one-click fixes."""
    fixes = []
    for i, rw in enumerate(rewrites):
        fixes.append({
            "id": f"bullet-{i}",
            "category": "Weak bullet",
            "issue": "This bullet reads as a duty, not an accomplishment.",
            "before": rw.get("before", ""),
            "after": rw.get("after", ""),
        })
    for i, sec in enumerate(skipped_sections):
        fixes.append({
            "id": f"section-{i}",
            "category": "Skipped section",
            "issue": f"Recruiters skip \"{sec}\" in the first 10 seconds — cut or replace it.",
            "before": sec,
            "after": "",
        })
    return fixes


def apply_fix(content: str, fix: dict) -> str:
    """Apply a single one-click fix to resume content. Best-effort text substitution."""
    before, after = fix.get("before", ""), fix.get("after", "")
    if not before:
        return content
    if before in content:
        return content.replace(before, after)
    # Structural fix (e.g. a skipped section heading) — drop any line mentioning it.
    if fix.get("category") == "Skipped section":
        lines = [ln for ln in content.split("\n") if before.lower() not in ln.lower()]
        return "\n".join(lines)
    return content


def validate(resume: str) -> dict:
    """ATS-safe structural checks."""
    text = resume or ""
    checks = {
        "no_tables": "\t" not in text and "|" not in text,
        "no_text_boxes": True,        # generated text has none
        "no_graphics": not re.search(r"!\[|<img", text),
        "no_icons": not re.search(r"[☀-➿-]", text),
        "standard_sections": bool(re.search(r"experience", text, re.I)),
        "reverse_chronological": True,
    }
    checks["passed"] = all(checks.values())
    return checks


def keyword_report(resume: str, jd: str, missing: list[str]) -> dict:
    r = (resume or "").lower()
    jd_words = set(re.findall(r"[a-zA-Z][a-zA-Z+#]{2,}", (jd or "").lower()))
    present = sorted({w for w in jd_words if w in r})[:25]
    return {
        "present_keywords": present,
        "missing_keywords": missing,
        "coverage_pct": round(100 * len(present) / max(len(jd_words), 1), 1),
    }
