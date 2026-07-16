from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.deps import get_current_user
from app.services import company as company_svc

router = APIRouter(prefix="/api/company", tags=["company"])


class CompanyIn(BaseModel):
    company: str
    context: str = ""


@router.post("/research")
def research(body: CompanyIn, user=Depends(get_current_user)):
    summary = (user.profile.career_goals if user.profile else "") + " " + body.context
    return company_svc.research(body.company, profile_summary=summary)
