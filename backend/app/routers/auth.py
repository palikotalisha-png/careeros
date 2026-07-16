from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import models, schemas
from app.deps import get_db, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup", response_model=schemas.Token)
def signup(body: schemas.SignUp, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = models.User(email=body.email, name=body.name,
                       hashed_password=pwd.hash(body.password))
    db.add(user); db.commit(); db.refresh(user)
    db.add(models.Profile(user_id=user.id)); db.commit()
    return schemas.Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=schemas.Token)
def login(body: schemas.Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not user.hashed_password or not pwd.verify(body.password,
                                                              user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return schemas.Token(access_token=create_access_token(user.id))


@router.get("/me")
def me(user: models.User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name}
