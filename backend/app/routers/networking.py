from fastapi import APIRouter, Depends
from app import schemas
from app.deps import get_current_user
from app.services import networking as net_svc

router = APIRouter(prefix="/api/networking", tags=["networking"])


@router.post("", response_model=schemas.OutreachOut)
def generate(body: schemas.OutreachIn, user=Depends(get_current_user)):
    summary = ((user.profile.career_goals if user.profile else "") + " " +
               (user.profile.resume_text[:500] if user.profile else ""))
    msg = net_svc.generate(body.kind, body.company, body.recruiter_name, body.recruiter_role,
                           body.job_title, body.job_description, summary, body.context)
    return schemas.OutreachOut(kind=body.kind, message=msg)
