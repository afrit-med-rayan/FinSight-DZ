from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.schemas.account import AccountResponse
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=List[AccountResponse])
def get_my_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts

@router.get("/{id}/balance-history")
def get_balance_history(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"date": "2025-01-01", "balance": 10000}]
