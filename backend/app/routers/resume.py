from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services import resume_ats
from app.services.files import to_pdf, to_docx

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/optimize", response_model=schemas.ResumeOut)
def optimize(body: schemas.ResumeOptimizeIn, db: Session = Depends(get_db),
             user=Depends(get_current_user)):
    resume = body.resume_text or (user.profile.resume_text if user.profile else "")
    r = resume_ats.optimize(resume, body.job_description, body.company)
    rv = models.ResumeVersion(
        user_id=user.id, job_id=body.job_id, label=f"Tailored — {body.company or 'role'}",
        content=r["content"], ats_score=r["ats_score"],
        recruiter_score=r["recruiter_score"], ats_score_before=r["ats_score_before"],
        missing_keywords=r["missing_keywords"], weak_bullets=r["weak_bullets"],
        improvements=r["improvements"], validation=r["validation"],
        keyword_report=r["keyword_report"], fixes=r["fixes"])
    db.add(rv); db.commit(); db.refresh(rv)
    return rv


@router.post("/{rid}/apply-fix", response_model=schemas.ResumeOut)
def apply_fix(rid: str, body: schemas.ApplyFixIn, db: Session = Depends(get_db),
              user=Depends(get_current_user)):
    rv = db.get(models.ResumeVersion, rid)
    if not rv or rv.user_id != user.id:
        raise HTTPException(404, "Not found")
    fix = next((f for f in rv.fixes if f["id"] == body.fix_id), None)
    if not fix:
        raise HTTPException(404, "Fix not found")
    if body.fix_id in rv.applied_fix_ids:
        return rv
    rv.content = resume_ats.apply_fix(rv.content, fix)
    rv.applied_fix_ids = rv.applied_fix_ids + [body.fix_id]
    rv.keyword_report = resume_ats.keyword_report(rv.content, "", rv.missing_keywords)
    rv.validation = resume_ats.validate(rv.content)
    rv.ats_score = min(100, rv.ats_score + 3)   # incremental credit per applied fix
    db.commit(); db.refresh(rv)
    return rv


@router.get("/versions", response_model=list[schemas.ResumeOut])
def versions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (db.query(models.ResumeVersion).filter_by(user_id=user.id)
            .order_by(models.ResumeVersion.created_at.desc()).all())


@router.get("/{rid}/export.{fmt}")
def export(rid: str, fmt: str, db: Session = Depends(get_db),
           user=Depends(get_current_user)):
    rv = db.get(models.ResumeVersion, rid)
    if not rv or rv.user_id != user.id:
        raise HTTPException(404, "Not found")
    if fmt == "pdf":
        return Response(to_pdf(rv.content, "Resume"), media_type="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=resume.pdf"})
    if fmt == "docx":
        return Response(
            to_docx(rv.content, "Resume"),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=resume.docx"})
    raise HTTPException(400, "fmt must be pdf or docx")
