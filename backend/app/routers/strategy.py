"""AI Career Coach: weekly strategy, salary range estimate, and interview-chance estimate."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.deps import get_db, get_current_user
from app.services.strategy import weekly_strategy

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.get("")
def get_strategy(db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = user.profile
    apps = db.query(models.Application).filter_by(user_id=user.id).all()

    profile_summary = ""
    if profile:
        profile_summary = (
            f"{profile.degree} in {profile.major}, GPA {profile.gpa}, "
            f"visa {profile.visa_status}, OPT {profile.opt_eligible}, "
            f"STEM OPT {profile.stem_opt_eligible}, skills: {', '.join(profile.skills or [])}, "
            f"target salary {profile.salary_min}-{profile.salary_max}, "
            f"locations: {', '.join(profile.preferred_locations or [])}, "
            f"industries: {', '.join(profile.desired_industries or [])}"
        )

    stats = {
        "total_applications": len(apps),
        "interviews": len([a for a in apps if a.status in ("Interview", "Final Round")]),
        "offers": len([a for a in apps if a.status in ("Offer", "Accepted")]),
        "rejections": len([a for a in apps if a.status == "Rejected"]),
    }
    recent_jobs = [a.job_title for a in apps[:10] if a.job_title]

    result = weekly_strategy(profile_summary, stats, recent_jobs)
    result.setdefault("estimated_salary_range", {"low": None, "high": None, "currency": "USD"})
    result.setdefault("interview_chance_pct", None)
    return result
