"""AIClient — single entry point for all LLM calls.

If OPENAI_API_KEY is set, calls the OpenAI Chat Completions API requesting JSON.
Otherwise falls back to a deterministic mock so the entire product runs offline
and tests stay stable. Swap the provider here without touching any service.
"""
from __future__ import annotations
import hashlib
import json
import re
from typing import Any
from app.config import settings


# ─────────────────────────── Prompt library (from product spec) ───────────────────────────
RECRUITER_ANALYSIS_PROMPT = """Act as a senior recruiter for {company}. Analyze the resume \
against this job description and return JSON with keys: match_score (0-100), \
missing_keywords (top 5), red_flags (top 3 a hiring manager notices in <10s), \
matching_qualifications, experience_gaps, recommendations.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}"""

RESUME_REWRITE_PROMPT = """Rewrite the experience section to naturally include the missing \
keywords and remove the red flags. Use the Google XYZ formula: "Accomplished X as measured \
by Y by doing Z." Strong action verbs, quantified achievements, ATS-friendly, natural \
language, NO keyword stuffing, NO fabricated information. Return JSON: {{"rewritten": "...", \
"changes": ["..."]}}.

MISSING KEYWORDS: {keywords}
RED FLAGS TO REMOVE: {red_flags}
EXPERIENCE SECTION:
{resume}"""

ATS_SCAN_PROMPT = """Act as an ATS filter AND a hiring manager reading 200 resumes in one \
sitting. Scan this resume. Return JSON: {{"ats_score": 0-100, "skipped_sections": ["..."], \
"weak_bullets": ["..."], "rewrites": [{{"before": "...", "after": "..."}}], \
"improvements": ["..."]}}.

RESUME:
{resume}"""

SOURCED_QUESTIONS_PROMPT = """You are compiling REAL, candidate-reported interview questions \
for {company} ({role}) from the public web search results below (Reddit, Glassdoor, Indeed, \
Blind, and similar review/forum threads). ONLY extract questions that are explicitly stated or \
clearly implied in the snippets — do NOT invent questions that aren't grounded in the results. \
If a result doesn't contain an identifiable question, skip it. For each question you extract, \
cite the exact source and add coaching notes.

Return JSON: {{"questions": [{{"question": "...", "source_title": "...", "source_url": "...", \
"source_domain": "...", "why_they_ask": "...", "strong_answer_includes": ["..."], \
"personalized_star": "..."}}]}}

SEARCH RESULTS (title | domain | snippet | url):
{snippets}

CANDIDATE RESUME:
{resume}"""


class AIClient:
    def __init__(self) -> None:
        self.enabled = bool(settings.openai_api_key)
        self._client = None
        if self.enabled:
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.openai_api_key)

    # ── public ──
    def json(self, system: str, prompt: str, *, seed_key: str = "") -> dict[str, Any]:
        """Return a JSON object from the model (or deterministic mock)."""
        if self.enabled:
            resp = self._client.chat.completions.create(
                model=settings.openai_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system + " Always reply with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            return json.loads(resp.choices[0].message.content)
        return self._mock(system, prompt, seed_key or prompt)

    def text(self, system: str, prompt: str, *, seed_key: str = "") -> str:
        if self.enabled:
            resp = self._client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
            )
            return resp.choices[0].message.content
        return self._mock_text(prompt, seed_key or prompt)

    # ── deterministic mock ──
    @staticmethod
    def _rng(seed: str, lo: int, hi: int) -> int:
        h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        return lo + (h % (hi - lo + 1))

    def _mock(self, system: str, prompt: str, seed: str) -> dict[str, Any]:
        s = system.lower()
        base = self._rng(seed, 58, 92)
        kws = self._keywords(prompt)
        # Order matters: check the most specific system-prompt signatures first, since
        # some prompts incidentally contain a later branch's keyword (e.g. a career
        # strategist prompt that lists "recruiters_to_contact" as a JSON key).
        if "strategist" in s or "career coach" in s:
            return self._mock_strategy(seed)
        if "recruiter" in s or "match" in s:
            return {
                "match_score": base,
                "missing_keywords": kws[:5],
                "red_flags": [
                    "No quantified impact in the top third of the resume",
                    "Generic summary not tailored to the role",
                    "Skills section buried below the fold",
                ],
                "matching_qualifications": [
                    "Relevant degree and coursework",
                    "Hands-on project experience",
                    "Demonstrated initiative",
                ],
                "experience_gaps": ["Limited industry experience", "Few leadership signals"],
                "recommendations": [
                    "Lead bullets with measurable outcomes",
                    f"Surface keywords: {', '.join(kws[:3])}",
                    "Move skills section above the fold",
                ],
            }
        if "ats" in s or "filter" in s:
            return {
                "ats_score": base,
                "skipped_sections": ["Objective", "References available on request"],
                "weak_bullets": [
                    "Responsible for various tasks",
                    "Worked on team projects",
                ],
                "rewrites": [
                    {
                        "before": "Responsible for various tasks",
                        "after": "Accomplished 30% faster onboarding as measured by ramp time "
                                 "by building an automated setup script",
                    }
                ],
                "improvements": [
                    "Use standard section headers (Experience, Education, Skills)",
                    "Single-column, no tables or text boxes",
                    f"Add keywords: {', '.join(kws[:4])}",
                ],
            }
        if "rewrite" in s:
            return {
                "rewritten": self._mock_text(prompt, seed),
                "changes": [
                    "Reframed bullets with the XYZ formula",
                    f"Worked in keywords: {', '.join(kws[:3])}",
                    "Removed unquantified claims",
                ],
            }
        if "sponsor" in s or "visa" in s:
            score = self._rng(seed, 35, 95)
            prob = "High" if score >= 70 else "Medium" if score >= 45 else "Low"
            return {
                "sponsorship_score": score,
                "sponsorship_probability": prob,
                "summary": "Estimated from H-1B/E-Verify history and role signals.",
                "risk_flags": [],
            }
        if "interview" in s:
            return {"questions": self._mock_questions(prompt, seed)}
        if "company" in s or "research" in s:
            return self._mock_company(prompt)
        return {"result": self._mock_text(prompt, seed), "score": base, "keywords": kws[:5]}

    def _mock_text(self, prompt: str, seed: str) -> str:
        return (
            "Accomplished a 25% improvement in pipeline throughput as measured by weekly "
            "deploys by introducing automated testing and CI; led a 4-person team to ship a "
            "data dashboard that cut reporting time from 3 days to 2 hours."
        )

    @staticmethod
    def _keywords(text: str) -> list[str]:
        common = {
            "python", "sql", "java", "react", "aws", "docker", "kubernetes", "machine",
            "learning", "data", "api", "agile", "tableau", "excel", "communication",
            "leadership", "analytics", "cloud", "etl", "typescript",
        }
        words = re.findall(r"[a-zA-Z]+", text.lower())
        found = [w for w in words if w in common]
        seen, out = set(), []
        for w in found:
            if w not in seen:
                seen.add(w); out.append(w.capitalize())
        defaults = ["Python", "SQL", "Cloud", "Stakeholder management", "CI/CD"]
        return (out + defaults)[:8]

    @staticmethod
    def _mock_questions(prompt: str, seed: str) -> list[dict]:
        def q(text, cat):
            return {
                "question": text,
                "category": cat,
                "why_they_ask": "Probes fit, depth, and how you think under pressure.",
                "strong_answer_includes": [
                    "Specific situation and your role",
                    "Concrete actions you took",
                    "Quantified result",
                ],
                "framework": "STAR: Situation → Task → Action → Result",
                "personalized_star": (
                    "S: In my capstone project the data pipeline kept failing. "
                    "T: I owned reliability. A: I added retries and monitoring. "
                    "R: Cut failures 90% and shipped on time."
                ),
            }
        return [
            q("Tell me about yourself.", "behavioral"),
            q("Describe a time you overcame a major obstacle.", "behavioral"),
            q("Why this company and this role?", "company"),
            q("Walk me through a project you're proud of.", "technical"),
            q("How would you design a scalable data pipeline?", "technical"),
            q("Tell me about a conflict on a team and how you handled it.", "behavioral"),
        ]

    @staticmethod
    def _mock_strategy(seed: str) -> dict:
        lo = AIClient._rng(seed, 60, 90) * 1000
        hi = lo + AIClient._rng(seed + "hi", 15, 35) * 1000
        chance = AIClient._rng(seed + "chance", 20, 75)
        return {
            "weekly_plan": [
                "Apply to 8-10 roles matched at 70+ with sponsorship signal",
                "Send 5 referral/recruiter outreach messages",
                "Complete 2 mock interviews for your top-funnel roles",
            ],
            "top_jobs_to_apply": [
                "Roles posted in the last 7 days at sponsorship-friendly companies",
                "Roles matching your strongest 3 skills first",
            ],
            "top_companies": ["Companies with recent H-1B filings in your target industry"],
            "skills_to_learn": ["SQL for analytics roles", "Cloud fundamentals (AWS or GCP)"],
            "certifications": ["AWS Cloud Practitioner", "Google Data Analytics Certificate"],
            "networking_recommendations": [
                "Message 3 alumni at target companies this week",
                "Attend one virtual info session for a target employer",
            ],
            "recruiters_to_contact": ["University recruiters listed on target companies' careers pages"],
            "alumni_to_contact": ["Alumni from your program working in your target industry"],
            "estimated_salary_range": {"low": lo, "high": hi, "currency": "USD"},
            "interview_chance_pct": chance,
        }

    @staticmethod
    def _mock_company(prompt: str) -> dict:
        return {
            "overview": {
                "what_they_do": "Builds enterprise software products.",
                "products": ["Core platform", "Analytics suite"],
                "services": ["Implementation", "Support"],
                "industry": "Technology",
                "headquarters": "United States",
                "size": "1,000-5,000",
                "revenue": "Not disclosed",
            },
            "business_intelligence": {
                "recent_news": ["Launched a new AI feature", "Expanded to EMEA"],
                "recent_earnings": "Revenue up year over year",
                "acquisitions": ["Acquired a small analytics startup"],
                "strategic_initiatives": ["AI investment", "Enterprise expansion"],
                "market_position": "Established mid-market player",
            },
            "career_intelligence": {
                "culture": "Collaborative, fast-paced",
                "values": ["Customer focus", "Ownership", "Inclusion"],
                "leadership": "Experienced product-led executive team",
                "hiring_trends": "Actively hiring across engineering and data",
                "sponsorship_history": "Has filed H-1B petitions in recent years",
                "international_hiring_patterns": "Hires international talent for technical roles",
            },
            "personalized_insight": (
                "Your data/analytics background and project work align with their current "
                "hiring in engineering, and their H-1B history makes sponsorship plausible."
            ),
        }


ai = AIClient()
