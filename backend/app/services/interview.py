from app.services.ai import ai


def generate(company: str, role: str, jd: str, resume: str) -> list[dict]:
    res = ai.json(
        "You are an interview prep coach. Generate a mix of candidate-reported, "
        "AI-predicted, behavioral, technical, and company questions. Return JSON "
        "{\"questions\": [{question, category, why_they_ask, strong_answer_includes, "
        "framework, personalized_star}]}.",
        f"Company: {company}\nRole: {role}\nJob description: {jd}\nCandidate resume: {resume}",
        seed_key=f"iv:{company}:{role}",
    )
    return res.get("questions", [])


def feedback(question: str, answer: str) -> dict:
    res = ai.json(
        "You are an interview coach giving structured feedback. Return JSON with "
        "score (0-100), strengths, improvements, improved_answer.",
        f"QUESTION: {question}\nCANDIDATE ANSWER: {answer}\n"
        "Evaluate using the STAR method and clarity, specificity, and impact.",
        seed_key=f"fb:{hash(answer) & 0xffff}",
    )
    res.setdefault("score", 70)
    res.setdefault("strengths", ["Clear structure"])
    res.setdefault("improvements", ["Add a quantified result", "Tighten the situation setup"])
    res.setdefault(
        "improved_answer",
        "S: ... T: ... A: ... R: increased X by Y% — keep it specific and measurable.",
    )
    return res
