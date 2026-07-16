"""The primary CareerOS flow: resume + (JD or URL) -> full analysis bundle."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.ingest import fetch_job_description
from app.services import resume_ats, company as company_svc, interview as interview_svc
from app.services import package as package_svc
from app.services.sponsorship import score_sponsorship
from app.services.matching import score_job

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


class AnalyzeIn(BaseModel):
    resume_text: str = ""          # falls back to saved profile resume
    job_description: str = ""
    job_url: str = ""
    company: str = ""
    job_title: str = ""
    save: bool = False


@router.post("")
def analyze(body: AnalyzeIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = user.profile
    resume = body.resume_text or (profile.resume_text if profile else "")

    jd, company, title = body.job_description, body.company, body.job_title
    if body.job_url and not jd:
        fetched = fetch_job_description(body.job_url)
        jd = fetched.get("description", "")
        company = company or fetched.get("company", "")
        title = title or fetched.get("title", "")

    # Persist a lightweight Job row so other features can reference it
    import hashlib
    h = hashlib.sha256(f"{title}|{company}|{jd[:200]}".encode()).hexdigest()
    job = db.query(models.Job).filter(models.Job.dedup_hash == h).first()
    if not job:
        job = models.Job(title=title or "Pasted role", company_name=company or "Unknown",
                         description=jd, source="paste", apply_url=body.job_url,
                         dedup_hash=h, e_verify=None)
        db.add(job); db.commit(); db.refresh(job)

    # Run the engines
    resume_report = resume_ats.optimize(resume, jd, company)
    spons = score_sponsorship(company, job, user, db)
    match = score_job(user, job)
    research = company_svc.research(
        company, profile_summary=(profile.career_goals if profile else ""))
    questions = interview_svc.generate(company, title, jd, resume)

    bundle = {
        "job": {"id": job.id, "title": job.title, "company": job.company_name,
                "url": job.apply_url},
        "resume_analysis": {
            "match_score": resume_report["recruiter_score"],
            "ats_score": resume_report["ats_score"],
            "ats_score_before": resume_report["ats_score_before"],
            "missing_keywords": resume_report["missing_keywords"],
            "red_flags": resume_report.get("rewrites") and [] or [],
            "strengths": resume_report["matching_qualifications"],
            "experience_gaps": resume_report["experience_gaps"],
            "recommendations": resume_report["improvements"],
            "weak_bullets": resume_report["weak_bullets"],
            "skipped_sections": resume_report["skipped_sections"],
            "optimized_resume": resume_report["content"],
            "validation": resume_report["validation"],
            "keyword_report": resume_report["keyword_report"],
            "fixes": resume_report["fixes"],
        },
        "match": match,
        "sponsorship": spons,
        "company_research": research,
        "interview": {"questions": questions},
    }

    if body.save:
        existing = (db.query(models.Application)
                    .filter_by(user_id=user.id, job_id=job.id).first())
        if not existing:
            from datetime import date
            db.add(models.Application(
                user_id=user.id, job_id=job.id, company=job.company_name,
                job_title=job.title, source="paste", status="Saved",
                date_found=date.today()))
            db.commit()
    return bundle


@router.post("/package")
def download_package(body: schemas.PackageIn, db: Session = Depends(get_db),
                      user=Depends(get_current_user)):
    """Bundle resume (PDF/DOCX) + cover letter + interview guide + company research +
    ATS report + follow-up/thank-you templates into one downloadable zip."""
    profile = user.profile
    resume_text = profile.resume_text if profile else ""

    job = db.get(models.Job, body.job_id) if body.job_id else None
    company = body.company or (job.company_name if job else "")
    job_title = body.job_title or (job.title if job else "")
    jd = body.job_description or (job.description if job else "")

    rv = db.get(models.ResumeVersion, body.resume_version_id) if body.resume_version_id else None
    if rv and rv.user_id != user.id:
        raise HTTPException(404, "Resume version not found")
    cl = db.get(models.CoverLetter, body.cover_letter_id) if body.cover_letter_id else None
    if cl and cl.user_id != user.id:
        raise HTTPException(404, "Cover letter not found")

    zip_bytes = package_svc.build(
        company=company, job_title=job_title, job_description=jd, resume=resume_text,
        resume_version=rv, cover_letter=cl,
        user_summary=profile.career_goals if profile else "",
    )
    fn = f"application_package_{(company or 'role').replace(' ', '_')}.zip"
    return Response(zip_bytes, media_type="application/zip",
                    headers={"Content-Disposition": f"attachment; filename={fn}"})
