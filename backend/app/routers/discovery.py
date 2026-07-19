from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.deps import get_db
from app.services import discovery as discovery_svc

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


def _check_cron_auth(authorization: str | None) -> None:
    """Vercel Cron sends `Authorization: Bearer <CRON_SECRET>` automatically when the
    CRON_SECRET env var is set on the project. If it isn't set (local dev), allow the call
    through so `python -m app.seed`-style manual testing keeps working."""
    if not settings.cron_secret:
        return
    if authorization != f"Bearer {settings.cron_secret}":
        raise HTTPException(401, "Unauthorized")


@router.post("/run")
def run_discovery(authorization: str | None = Header(None), db: Session = Depends(get_db)):
    _check_cron_auth(authorization)
    return discovery_svc.run(db)
