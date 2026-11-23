"""
DOOM AI — JWT Authentication
Registration persists users. Login verifies password.
Public registration cannot assign privileged roles.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import SessionLocal
from config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()

PRIVILEGED_ROLES = {"owner", "admin", "founder"}
DEFAULT_ROLE = "member"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = DEFAULT_ROLE

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "iss": "doom-ai", "typ": "access"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def get_user_by_email(db: Session, email: str):
    row = db.execute(text("SELECT id, email, password_hash, role FROM users WHERE email = :email"), {"email": email}).fetchone()
    if not row:
        return None
    return {"id": row[0], "email": row[1], "password_hash": row[2], "role": row[3]}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "role": payload.get("role", DEFAULT_ROLE)}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Reject privileged roles from public registration
    role = user.role.lower().strip() if user.role else DEFAULT_ROLE
    if role in PRIVILEGED_ROLES:
        raise HTTPException(status_code=403, detail="Cannot self-assign privileged role")

    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(user.password)
    db.execute(
        text("INSERT INTO users (email, password_hash, role) VALUES (:email, :pw, :role)"),
        {"email": user.email, "pw": hashed, "role": role},
    )
    db.commit()

    token = create_access_token({"sub": user.email, "role": role})
    return {"access_token": token, "token_type": "bearer", "expires_in": settings.jwt_expire_minutes * 60}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if not existing:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(user.password, existing["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": existing["email"], "role": existing["role"]})
    return {"access_token": token, "token_type": "bearer", "expires_in": settings.jwt_expire_minutes * 60}

@router.get("/me")
async def me(current = Depends(get_current_user)):
    return current
