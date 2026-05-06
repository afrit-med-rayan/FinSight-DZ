from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.account import Account, AccountType
from app.schemas.auth import UserCreate, UserResponse, Token
from app.seed.seed_transactions import generate_demo_data
from app.services.insight_engine import generate_insights
import random

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def generate_rib(bank_code: str = "007", branch_code: str = "00001") -> str:
    account_number = str(random.randint(10000000000, 99999999999))
    base = bank_code + branch_code + account_number
    key = 97 - (int(base) % 97)
    key_str = str(key).zfill(2)
    return base + key_str

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = pwd_context.hash(user_in.password)
    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_pw,
        wilaya_code=user_in.wilaya_code
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    rib = generate_rib()
    ccp_account = Account(
        user_id=user.id,
        rib=rib,
        account_type=AccountType.CCP,
    )
    db.add(ccp_account)
    db.commit()
    db.refresh(ccp_account)

    generate_demo_data(ccp_account.id, user.salary_day, db)

    # Run initial insight generation so the new user has insights from day 1
    try:
        generate_insights(ccp_account.id, db)
    except Exception:
        pass  # Never block registration if insight generation fails

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password", headers={"error_code": "INVALID_CREDENTIALS"})
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
