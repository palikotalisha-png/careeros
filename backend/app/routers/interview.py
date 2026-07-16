from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user
from app.services import interview as interview_svc
from app.services import hirevue as hirevue_svc

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/prep", response_model=schemas.InterviewOut)
def prep(body: schemas.InterviewIn, db: Session = Depends(get_db),
         user=Depends(get_current_user)):
    resume = user.profile.resume_text if user.profile else ""
    qs = interview_svc.generate(body.company, body.role, body.job_description, resume)
    ip = models.InterviewPrep(user_id=user.id, job_id=body.job_id, company=body.company,
                              role=body.role, kind="general", questions=qs)
    db.add(ip); db.commit(); db.refresh(ip)
    return ip


@router.post("/feedback")
def feedback(body: schemas.MockAnswerIn, user=Depends(get_current_user)):
    return interview_svc.feedback(body.question, body.answer)


@router.post("/hirevue", response_model=schemas.HireVueOut)
def hirevue_prep(body: schemas.HireVueIn, db: Session = Depends(get_db),
                  user=Depends(get_current_user)):
    resume = user.profile.resume_text if user.profile else ""
    r = hirevue_svc.generate(body.company, body.role, body.job_description, resume)
    ip = models.InterviewPrep(user_id=user.id, job_id=body.job_id, company=body.company,
                              role=body.role, kind="hirevue",
                              questions=r["questions"], live=r.get("live", False),
                              note=r.get("note", ""))
    db.add(ip); db.commit(); db.refresh(ip)
    return ip
