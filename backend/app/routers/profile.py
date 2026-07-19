from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.files import parse_resume

MIN_USABLE_CHARS = 40   # below this, treat extraction as effectively empty

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _ensure(db, user):
    if not user.profile:
        p = models.Profile(user_id=user.id); db.add(p); db.commit(); db.refresh(user)
    return user.profile


@router.get("", response_model=schemas.ProfileOut)
def get_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return _ensure(db, user)


@router.put("", response_model=schemas.ProfileOut)
def update_profile(body: schemas.ProfileIn, db: Session = Depends(get_db),
                   user=Depends(get_current_user)):
    p = _ensure(db, user)
    for k, v in body.model_dump().items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p


@router.post("/resume", response_model=schemas.ResumeUploadOut)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db),
                        user=Depends(get_current_user)):
    p = _ensure(db, user)
    data = await file.read()
    if not data:
        raise HTTPException(400, "That file appears to be empty. Please choose a different file.")

    try:
        text = parse_resume(file.filename, data)
    except Exception:
        raise HTTPException(
            400,
            "We couldn't read that file — it may be corrupted or not a real PDF/DOCX. "
            "Try re-saving/exporting it, or paste your resume text directly below instead.",
        )

    p.resume_text = text
    p.resume_filename = file.filename
    db.commit(); db.refresh(p)

    warning = None
    if len(text.strip()) < MIN_USABLE_CHARS:
        warning = (
            "We uploaded your file, but couldn't find readable text in it — this usually "
            "means it's a scanned image rather than a real text document. Every AI feature "
            "(matching, ATS scoring, etc.) needs actual text, so please paste your resume "
            "into the box below."
        )
    return schemas.ResumeUploadOut(profile=p, warning=warning)
