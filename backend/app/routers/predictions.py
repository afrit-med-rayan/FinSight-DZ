from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/next-month")
def get_prediction(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"predicted_for_month": "2025-07", "predicted_expense_da": 0, "predicted_balance_da": 0, "confidence_interval_da": 0, "model_version": "linear_v1"}
