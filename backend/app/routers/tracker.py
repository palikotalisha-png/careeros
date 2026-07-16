from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/applications", tags=["tracker"])
STATUSES = ["Saved", "Applying", "Applied", "Assessment", "Recruiter Screen",
            "Interview", "Final Round", "Follow-up", "Rejected", "Offer", "Accepted"]


@router.get("", response_model=list[schemas.ApplicationOut])
def list_apps(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (db.query(models.Application).filter_by(user_id=user.id)
            .order_by(models.Application.created_at.desc()).all())


@router.post("", response_model=schemas.ApplicationOut)
def create(body: schemas.ApplicationIn, db: Session = Depends(get_db),
           user=Depends(get_current_user)):
    app = models.Application(user_id=user.id, **body.model_dump())
    db.add(app); db.commit(); db.refresh(app)
    return app


@router.put("/{aid}", response_model=schemas.ApplicationOut)
def update(aid: str, body: schemas.ApplicationIn, db: Session = Depends(get_db),
           user=Depends(get_current_user)):
    app = db.get(models.Application, aid)
    if not app or app.user_id != user.id:
        raise HTTPException(404, "Not found")
    for k, v in body.model_dump().items():
        setattr(app, k, v)
    db.commit(); db.refresh(app)
    return app


@router.delete("/{aid}")
def delete(aid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    app = db.get(models.Application, aid)
    if not app or app.user_id != user.id:
        raise HTTPException(404, "Not found")
    db.delete(app); db.commit()
    return {"ok": True}
