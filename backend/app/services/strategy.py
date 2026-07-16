from app.services.ai import ai


def weekly_strategy(profile_summary: str, app_stats: dict, recent_jobs: list[str]) -> dict:
    res = ai.json(
        "You are a career strategist for international students. Return JSON with keys: "
        "weekly_plan, top_jobs_to_apply, top_companies, skills_to_learn, certifications, "
        "networking_recommendations, recruiters_to_contact, alumni_to_contact.",
        f"Candidate: {profile_summary}\nApplication stats: {app_stats}\n"
        f"Recent matched jobs: {', '.join(recent_jobs[:10])}\n"
        "Prioritize highest-probability, sponsorship-friendly opportunities.",
        seed_key=f"strat:{hash(profile_summary) & 0xffff}",
    )
    return res
