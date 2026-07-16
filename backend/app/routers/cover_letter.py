from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.ai import ai
from app.services.files import to_pdf, to_docx

router = APIRouter(prefix="/api/cover-letter", tags=["cover_letter"])


@router.post("", response_model=schemas.CoverLetterOut)
def generate(body: schemas.CoverLetterIn, db: Session = Depends(get_db),
             user=Depends(get_current_user)):
    resume = user.profile.resume_text if user.profile else ""
    name = user.name or "the candidate"
    content = ai.text(
        "You write authentic, human-sounding cover letters. Natural tone, specific, no clichés.",
        f"Write a personalized, professional cover letter ({body.tone} tone) for {name} "
        f"applying to {body.company}. Base it on the candidate's real experience; do not "
        f"invent facts.\nJOB DESCRIPTION:\n{body.job_description}\nRESUME:\n{resume}",
        seed_key=f"cl:{body.company}:{user.id}")
    cl = models.CoverLetter(user_id=user.id, job_id=body.job_id, company=body.company,
                            content=content)
    db.add(cl); db.commit(); db.refresh(cl)
    return cl


@router.put("/{cid}", response_model=schemas.CoverLetterOut)
def edit(cid: str, content: dict, db: Session = Depends(get_db),
         user=Depends(get_current_user)):
    cl = db.get(models.CoverLetter, cid)
    if not cl or cl.user_id != user.id:
        raise HTTPException(404, "Not found")
    cl.content = content.get("content", cl.content); db.commit(); db.refresh(cl)
    return cl


@router.get("/{cid}/export.{fmt}")
def export(cid: str, fmt: str, db: Session = Depends(get_db),
           user=Depends(get_current_user)):
    cl = db.get(models.CoverLetter, cid)
    if not cl or cl.user_id != user.id:
        raise HTTPException(404, "Not found")
    fn = "cover_letter"
    if fmt == "pdf":
        return Response(to_pdf(cl.content, "Cover Letter"), media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename={fn}.pdf"})
    if fmt == "docx":
        return Response(
            to_docx(cl.content, "Cover Letter"),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={fn}.docx"})
    raise HTTPException(400, "fmt must be pdf or docx")
