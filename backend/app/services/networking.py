from app.services.ai import ai

_GUIDES = {
    "linkedin": "a concise, warm LinkedIn connection note (<300 chars)",
    "referral": "a polite referral request to an employee",
    "recruiter": "a professional outreach message to a recruiter",
    "thank_you": "a thank-you email after an interview",
    "follow_up": "a follow-up email checking on application status",
}


def generate(kind: str, company: str, recruiter_name: str, recruiter_role: str,
             job_title: str, jd: str, user_summary: str, context: str) -> str:
    guide = _GUIDES.get(kind, _GUIDES["linkedin"])
    return ai.text(
        "You write authentic, human-sounding professional outreach. No clichés, no fluff.",
        f"Write {guide}.\nTo: {recruiter_name} ({recruiter_role}) at {company}\n"
        f"Role of interest: {job_title}\nJob description: {jd}\n"
        f"About me: {user_summary}\nExtra context: {context}",
        seed_key=f"net:{kind}:{company}:{recruiter_name}",
    )
