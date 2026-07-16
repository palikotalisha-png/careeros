from datetime import datetime, timedelta
from typing import Generator
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
ALGORITHM = "HS256"
_jwks_cache: dict = {}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(user_id: str, days: int = 30) -> str:
    payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(days=days)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def _verify_clerk(token: str) -> dict | None:
    """Verify a Clerk session JWT via JWKS. Returns claims or None."""
    if not settings.clerk_jwks_url:
        return None
    global _jwks_cache
    if not _jwks_cache:
        _jwks_cache = httpx.get(settings.clerk_jwks_url, timeout=10).json()
    try:
        claims = jwt.decode(
            token, _jwks_cache, algorithms=["RS256"],
            issuer=settings.clerk_issuer or None,
            options={"verify_aud": False},
        )
        return claims
    except JWTError:
        return None


def _upsert_clerk_user(db: Session, claims: dict) -> models.User:
    sub = claims.get("sub")
    email = claims.get("email") or claims.get("email_address") or f"{sub}@clerk.user"
    user = db.query(models.User).filter(models.User.id == sub).first()
    if not user:
        user = models.User(id=sub, email=email, name=claims.get("name", ""),
                           auth_provider="clerk")
        db.add(user); db.commit(); db.refresh(user)
    return user


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    cred_err = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    if not token:
        raise cred_err

    # 1. Try Clerk (production)
    claims = _verify_clerk(token)
    if claims:
        return _upsert_clerk_user(db, claims)

    # 2. Dev credential JWT (scaffold)
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user = db.get(models.User, payload.get("sub"))
        if user:
            return user
    except JWTError:
        pass
    raise cred_err
