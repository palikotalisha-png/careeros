from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.sponsorship import score_sponsorship

router = APIRouter(prefix="/api/sponsorship", tags=["sponsorship"])


class SponsorshipIn(BaseModel):
    company: str
    job_description: str = ""


@router.post("", response_model=schemas.SponsorshipOut)
def analyze(body: SponsorshipIn, db: Session = Depends(get_db),
            user=Depends(get_current_user)):
    job = models.Job(title="", company_name=body.company, description=body.job_description)
    s = score_sponsorship(body.company, job, user, db)
    return schemas.SponsorshipOut(company=body.company, **{
        k: s[k] for k in ("sponsorship_score", "sponsorship_probability",
                          "intl_compat_score", "e_verify", "h1b_history",
                          "risk_flags", "summary")})
