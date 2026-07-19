from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.matching import score_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _get_or_score_match(db: Session, user: models.User, job: models.Job) -> models.JobMatch:
    match = db.query(models.JobMatch).filter_by(user_id=user.id, job_id=job.id).first()
    if match:
        return match
    scored = score_job(user, job)
    match = models.JobMatch(user_id=user.id, job_id=job.id, **scored)
    db.add(match); db.commit(); db.refresh(match)
    return match


@router.get("", response_model=list[schemas.JobWithMatch])
def list_jobs(
    min_match: int = Query(0, ge=0, le=100),
    sponsorship_only: bool = False,
    location: str = "",
    source: str = "",
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(models.Job).order_by(models.Job.created_at.desc())
    if location:
        q = q.filter(models.Job.location.ilike(f"%{location}%"))
    if source:
        q = q.filter(models.Job.source == source)
    jobs = q.limit(300).all()  # raw pull cap; score + filter below

    out = []
    for job in jobs:
        match = _get_or_score_match(db, user, job)
        if match.match_score < min_match:
            continue
        if sponsorship_only and match.sponsorship_probability == "Low":
            continue
        out.append(schemas.JobWithMatch(job=job, match=match))
        if len(out) >= limit:
            break
    return out


@router.get("/{job_id}", response_model=schemas.JobWithMatch)
def get_job(job_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(404, "Not found")
    match = _get_or_score_match(db, user, job)
    db.add(models.UserEvent(user_id=user.id, event_type="view", job_id=job.id))
    db.commit()
    return schemas.JobWithMatch(job=job, match=match)


@router.post("/{job_id}/save", response_model=schemas.ApplicationOut)
def save_job(job_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(404, "Not found")
    existing = db.query(models.Application).filter_by(user_id=user.id, job_id=job_id).first()
    if existing:
        return existing
    app_ = models.Application(
        user_id=user.id, job_id=job.id, company=job.company_name, job_title=job.title,
        location=job.location, source=job.source, status="Saved", date_found=date.today(),
        salary=job.salary, e_verify=job.e_verify,
    )
    db.add(app_); db.commit(); db.refresh(app_)
    db.add(models.UserEvent(user_id=user.id, event_type="save", job_id=job.id))
    db.commit()
    return app_


@router.get("/favorites/list")
def list_favorites(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(models.FavoriteCompany).filter_by(user_id=user.id).all()
    return [r.company_name for r in rows]


@router.post("/favorites/{company_name}")
def add_favorite(company_name: str, db: Session = Depends(get_db),
                 user=Depends(get_current_user)):
    exists = (db.query(models.FavoriteCompany)
              .filter_by(user_id=user.id, company_name=company_name).first())
    if not exists:
        db.add(models.FavoriteCompany(user_id=user.id, company_name=company_name))
        db.commit()
    return {"ok": True}


@router.delete("/favorites/{company_name}")
def remove_favorite(company_name: str, db: Session = Depends(get_db),
                    user=Depends(get_current_user)):
    (db.query(models.FavoriteCompany)
     .filter_by(user_id=user.id, company_name=company_name).delete())
    db.commit()
    return {"ok": True}
