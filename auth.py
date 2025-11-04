import os, jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from db import get_db
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))

class RegisterIn(BaseModel):
    full_name: str; email: EmailStr; password: str; role: str = "EMP"

class LoginIn(BaseModel):
    email: EmailStr; password: str

class ChangePwIn(BaseModel):
    old_password: str; new_password: str

def create_token(user: User):
    payload = {"sub": str(user.id), "email": user.email, "role": user.role,
               "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MIN)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def get_current_user(db: Session = Depends(get_db), token: str | None = None):
    from fastapi import Header
    def inner(authorization: str = Header(None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")
        token = authorization.split(" ", 1)[1]
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.get(User, int(data["sub"]))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    return inner

@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email already exists")
    user = User(full_name=payload.full_name, email=payload.email,
                password_hash=pwd.hash(payload.password), role=payload.role.upper())
    db.add(user); db.commit(); db.refresh(user)
    return {"ok": True, "user_id": user.id}

@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not pwd.verify(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(user)
    return {"ok": True, "token": token, "full_name": user.full_name, "role": user.role}

@router.post("/change-password")
def change_pw(payload: ChangePwIn, db: Session = Depends(get_db), me: User = Depends(get_current_user())):
    if not pwd.verify(payload.old_password, me.password_hash):
        raise HTTPException(400, "Old password incorrect")
    me.password_hash = pwd.hash(payload.new_password)
    db.commit()
    return {"ok": True}
