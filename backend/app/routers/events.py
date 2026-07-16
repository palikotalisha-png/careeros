from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.matching import update_preferences

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("")
def log_event(body: schemas.EventIn, db: Session = Depends(get_db),
              user=Depends(get_current_user)):
    db.add(models.UserEvent(user_id=user.id, event_type=body.event_type,
                            job_id=body.job_id, payload=body.payload))
    db.commit()
    # Update the learned preference vector
    events = db.query(models.UserEvent).filter_by(user_id=user.id).all()
    jobs = {j.id: j for j in db.query(models.Job).all()}
    if user.profile:
        user.profile.preference_vector = update_preferences(user.profile, events, jobs)
        db.commit()
    return {"ok": True}
