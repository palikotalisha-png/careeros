from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    apps = db.query(models.Application).filter_by(user_id=user.id).all()
    today = date.today()
    month_start = today.replace(day=1)
    active = [a for a in apps if a.status in (
        "Applying", "Applied", "Assessment", "Recruiter Screen",
        "Interview", "Final Round", "Follow-up")]
    resumes = (db.query(models.ResumeVersion).filter_by(user_id=user.id)
               .order_by(models.ResumeVersion.created_at).all())

    upcoming_interviews = sorted(
        [{"company": a.company, "job_title": a.job_title,
          "date": a.interview_date.isoformat()}
         for a in apps if a.interview_date and a.interview_date >= today],
        key=lambda x: x["date"])
    upcoming_followups = sorted(
        [{"company": a.company, "job_title": a.job_title,
          "date": a.follow_up_date.isoformat()}
         for a in apps if a.follow_up_date and a.follow_up_date >= today],
        key=lambda x: x["date"])

    funnel = {s: 0 for s in ["Saved", "Applying", "Applied", "Assessment",
                             "Recruiter Screen", "Interview", "Final Round",
                             "Follow-up", "Rejected", "Offer", "Accepted"]}
    for a in apps:
        funnel[a.status] = funnel.get(a.status, 0) + 1

    return {
        "active_applications": len(active),
        "applications_this_month": len([a for a in apps
                                        if a.date_applied and a.date_applied >= month_start]),
        "interview_count": funnel["Interview"] + funnel["Final Round"],
        "offer_count": funnel["Offer"] + funnel["Accepted"],
        "ats_score_trend": [{"label": r.label, "before": r.ats_score_before,
                             "after": r.ats_score} for r in resumes],
        "ats_improvement": (resumes[-1].ats_score - resumes[-1].ats_score_before)
                           if resumes else 0,
        "funnel": funnel,
        "response_rate": round(
            100 * (funnel["Assessment"] + funnel["Recruiter Screen"] + funnel["Interview"]
                   + funnel["Final Round"] + funnel["Offer"]) /
            max(funnel["Applied"] + funnel["Assessment"] + funnel["Recruiter Screen"] +
                funnel["Interview"] + funnel["Final Round"] + funnel["Offer"] +
                funnel["Rejected"], 1), 1),
        "upcoming_interviews": upcoming_interviews,
        "upcoming_followups": upcoming_followups,
    }
