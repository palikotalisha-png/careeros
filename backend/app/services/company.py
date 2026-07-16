from app.services.ai import ai


def research(company_name: str, profile_summary: str = "") -> dict:
    res = ai.json(
        "You are a company research analyst. Return JSON with keys overview, "
        "business_intelligence, career_intelligence, personalized_insight.",
        f"Research the company '{company_name}' for an international student job seeker.\n"
        f"Candidate background: {profile_summary}\n"
        f"Cover what they do, products, services, industry, HQ, size, revenue; recent news, "
        f"earnings, acquisitions, strategic initiatives, market position; culture, values, "
        f"leadership, hiring trends, sponsorship history, international hiring patterns; and "
        f"why this company may be a good fit for the candidate.",
        seed_key=f"company:{company_name}",
    )
    return res
