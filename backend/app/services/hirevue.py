"""Real, web-sourced interview questions: pulls candidate-reported questions for a specific
company/role from public search results (Reddit, Glassdoor, Indeed, Blind, etc.) instead of
generating them with an LLM. The AI is only used to add coaching notes to questions that are
already grounded in a real, cited source — it never invents the question text itself.

Requires SERPAPI_KEY (backend/.env) to fetch live results. Without a key, generate() returns
an honest "no live source connected" note rather than fabricating fake citations.
"""
from __future__ import annotations
import re
from app.services import search as search_svc
from app.services.ai import ai

QUESTION_MARKERS = ["asked me", "asked about", "asked to", "they asked", "was asked",
                     "interview question", "questions included", "how would you", "why do you"]


def _looks_like_question(snippet: str) -> bool:
    s = (snippet or "").lower()
    return "?" in snippet or any(m in s for m in QUESTION_MARKERS)


def _extract_question_text(snippet: str) -> str:
    """Prefer the sentence containing '?' if present, else the raw snippet."""
    if "?" in snippet:
        for part in re.split(r"(?<=[.?!])\s+", snippet):
            if "?" in part:
                return part.strip()
    return snippet.strip()


def generate(company: str, role: str, jd: str, resume: str) -> dict:
    if not search_svc.enabled():
        return {
            "questions": [],
            "live": False,
            "note": (
                "Connect a search API key (SERPAPI_KEY in backend/.env) to pull real, "
                f"candidate-reported {role or 'interview'} questions for "
                f"{company or 'this company'} from Reddit, Glassdoor, and Indeed reviews."
            ),
        }

    results = search_svc.search_reported_questions(company, role)
    candidates = [r for r in results if _looks_like_question(r.get("snippet", ""))][:8]
    if not candidates:
        return {
            "questions": [],
            "live": True,
            "note": f"No candidate-reported questions turned up in public search results "
                    f"for {company or 'this company'} right now — try again later or broaden "
                    f"the role title.",
        }

    snippet_block = "\n".join(
        f'{i + 1}. "{_extract_question_text(c["snippet"])}" — {c["title"]} '
        f'({c["domain"]}) {c["link"]}'
        for i, c in enumerate(candidates)
    )
    enriched = ai.json(
        "You add coaching notes to REAL, already-sourced candidate-reported interview "
        "questions. Do not invent new questions — only add why_they_ask, "
        "strong_answer_includes, and a personalized_star answer based on the candidate's "
        "resume, in the same order as the questions listed.",
        f"Company: {company}\nRole: {role}\nJob description: {jd}\n"
        f"Candidate resume: {resume}\n\nSOURCED QUESTIONS:\n{snippet_block}",
        seed_key=f"srcq:{company}:{role}",
    )
    coaching = enriched.get("questions", [])

    questions = []
    for i, c in enumerate(candidates):
        note = coaching[i] if i < len(coaching) else {}
        questions.append({
            "question": _extract_question_text(c["snippet"]),
            "source_title": c["title"],
            "source_url": c["link"],
            "source_domain": c["domain"],
            "why_they_ask": note.get(
                "why_they_ask", "Reported by past candidates as commonly asked for this role."),
            "strong_answer_includes": note.get("strong_answer_includes", [
                "Specific situation and your role", "Concrete actions you took",
                "Quantified result"]),
            "personalized_star": note.get("personalized_star", ""),
        })
    return {"questions": questions, "live": True}
