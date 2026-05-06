from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.routers.auth import get_current_user
from app.services.ml_predictor import train_and_predict
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PredictionOut(BaseModel):
    id: int
    predicted_for_month: str
    predicted_expense_da: float
    predicted_balance_da: float
    confidence_interval_da: float
    model_version: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PredictionOut])
def get_predictions(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ensure user owns the account (Optional but good)
    # Fetch existing predictions
    preds = db.query(Prediction).filter(Prediction.account_id == account_id).order_by(Prediction.predicted_for_month.asc()).all()
    
    # If no predictions, try to generate them on the fly
    if not preds:
        train_and_predict(account_id, db)
        preds = db.query(Prediction).filter(Prediction.account_id == account_id).order_by(Prediction.predicted_for_month.asc()).all()
        
    return preds

@router.post("/retrain")
def manual_retrain(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = train_and_predict(account_id, db)
    return {"status": "retrained", "count": len(results)}
