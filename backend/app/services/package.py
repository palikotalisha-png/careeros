"""One-click application package: zips resume, cover letter, interview guide, company
research, ATS report, and follow-up/thank-you email templates into a single download."""
from __future__ import annotations
import io
import zipfile
from app.services.files import to_pdf, to_docx
from app.services import company as company_svc, interview as interview_svc, networking


def _txt(title: str, body: str) -> str:
    return f"{title}\n{'=' * len(title)}\n\n{body}\n"


def _questions_to_text(questions: list[dict]) -> str:
    out = []
    for i, q in enumerate(questions, 1):
        out.append(
            f"{i}. {q.get('question', '')}  [{q.get('category', '')}]\n"
            f"   Why they ask: {q.get('why_they_ask', '')}\n"
            f"   Strong answer includes: {', '.join(q.get('strong_answer_includes', []))}\n"
            f"   Framework: {q.get('framework', '')}\n"
            f"   Sample STAR answer: {q.get('personalized_star', '')}\n"
        )
    return "\n".join(out)


def _research_to_text(r: dict) -> str:
    ov, bi, ci = r.get("overview", {}), r.get("business_intelligence", {}), r.get("career_intelligence", {})
    return (
        f"WHAT THEY DO\n{ov.get('what_they_do', '')}\n\n"
        f"Products: {', '.join(ov.get('products', []))}\n"
        f"Services: {', '.join(ov.get('services', []))}\n"
        f"Industry: {ov.get('industry', '')}\n"
        f"HQ: {ov.get('headquarters', '')}\n"
        f"Size: {ov.get('size', '')}\n"
        f"Revenue: {ov.get('revenue', '')}\n\n"
        f"BUSINESS INTELLIGENCE\n"
        f"Recent news: {', '.join(bi.get('recent_news', []))}\n"
        f"Recent earnings: {bi.get('recent_earnings', '')}\n"
        f"Acquisitions: {', '.join(bi.get('acquisitions', []))}\n"
        f"Strategic initiatives: {', '.join(bi.get('strategic_initiatives', []))}\n"
        f"Market position: {bi.get('market_position', '')}\n\n"
        f"CAREER INTELLIGENCE\n"
        f"Culture: {ci.get('culture', '')}\n"
        f"Values: {', '.join(ci.get('values', []))}\n"
        f"Leadership: {ci.get('leadership', '')}\n"
        f"Hiring trends: {ci.get('hiring_trends', '')}\n"
        f"Sponsorship history: {ci.get('sponsorship_history', '')}\n"
        f"International hiring patterns: {ci.get('international_hiring_patterns', '')}\n\n"
        f"WHY THIS COMPANY MAY FIT YOU\n{r.get('personalized_insight', '')}\n"
    )


def _ats_report_to_text(rv) -> str:
    return (
        f"Recruiter match score: {rv.recruiter_score}/100\n"
        f"ATS score: {rv.ats_score_before} -> {rv.ats_score}/100\n\n"
        f"Missing keywords: {', '.join(rv.missing_keywords)}\n\n"
        f"Weak bullets flagged:\n" + "\n".join(f"- {b}" for b in rv.weak_bullets) + "\n\n"
        f"Improvement suggestions:\n" + "\n".join(f"- {i}" for i in rv.improvements) + "\n\n"
        f"ATS validation: {'PASSED' if rv.validation.get('passed') else 'NEEDS REVIEW'}\n"
        f"Keyword coverage: {rv.keyword_report.get('coverage_pct', 0)}%\n"
    )


def build(*, company: str, job_title: str, job_description: str, resume: str,
          resume_version=None, cover_letter=None, user_summary: str = "") -> bytes:
    """Assemble the full application package as an in-memory zip and return its bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # Resume
        resume_content = resume_version.content if resume_version else resume
        z.writestr("resume.pdf", to_pdf(resume_content, "Resume"))
        z.writestr("resume.docx", to_docx(resume_content, "Resume"))

        # Cover letter
        if cover_letter:
            z.writestr("cover_letter.pdf", to_pdf(cover_letter.content, "Cover Letter"))
            z.writestr("cover_letter.docx", to_docx(cover_letter.content, "Cover Letter"))

        # Interview prep guide
        questions = interview_svc.generate(company, job_title, job_description, resume_content)
        z.writestr("interview_prep_guide.txt",
                    _txt(f"Interview Prep — {job_title} at {company}",
                         _questions_to_text(questions)))

        # Company research
        research = company_svc.research(company, profile_summary=user_summary)
        z.writestr("company_research.txt",
                    _txt(f"Company Research — {company}", _research_to_text(research)))

        # ATS report
        if resume_version:
            z.writestr("ats_report.txt",
                        _txt(f"ATS Report — {job_title} at {company}",
                             _ats_report_to_text(resume_version)))

        # Follow-up + thank-you templates
        follow_up = networking.generate("follow_up", company, "", "", job_title,
                                        job_description, user_summary, "")
        thank_you = networking.generate("thank_you", company, "", "", job_title,
                                        job_description, user_summary, "")
        z.writestr("follow_up_email.txt", _txt("Follow-up Email Template", follow_up))
        z.writestr("thank_you_email.txt", _txt("Thank-You Email Template", thank_you))

    return buf.getvalue()
