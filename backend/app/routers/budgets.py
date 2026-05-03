from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.routers.auth import get_current_user
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

router = APIRouter()

class BudgetCreate(BaseModel):
    account_id: int
    category_id: int
    limit_da: Decimal
    period_type: str = "MENSUEL"
    start_date: date

class BudgetOut(BaseModel):
    id: int
    account_id: int
    category_id: int
    limit_da: Decimal
    period_type: str
    start_date: date
    is_active: bool
    spent_da: Optional[float] = 0.0
    remaining_da: Optional[float] = 0.0
    class Config:
        from_attributes = True

@router.get("/", response_model=List[BudgetOut])
def get_budgets(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    budgets = db.query(Budget).filter(Budget.account_id == account_id, Budget.is_active == True).all()
    result = []
    for b in budgets:
        spent = float(db.query(func.sum(Transaction.amount_da)).filter(
            Transaction.account_id == account_id,
            Transaction.category_id == b.category_id,
            Transaction.type == "DEBIT",
            Transaction.status == "COMPLETED",
        ).scalar() or 0)
        out = BudgetOut.model_validate(b)
        out.spent_da = spent
        out.remaining_da = max(0, float(b.limit_da) - spent)
        result.append(out)
    return result

@router.post("/", response_model=BudgetOut)
def create_budget(budget_in: BudgetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = Budget(**budget_in.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

@router.delete("/{id}")
def delete_budget(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Budget).filter(Budget.id == id).first()
    if b:
        db.delete(b)
        db.commit()
    return {"ok": True}
