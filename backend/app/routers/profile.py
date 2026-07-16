from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.files import parse_resume

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


@router.post("/resume", response_model=schemas.ProfileOut)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db),
                        user=Depends(get_current_user)):
    p = _ensure(db, user)
    data = await file.read()
    p.resume_text = parse_resume(file.filename, data)
    p.resume_filename = file.filename
    db.commit(); db.refresh(p)
    return p
