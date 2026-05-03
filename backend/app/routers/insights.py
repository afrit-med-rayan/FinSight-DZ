from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.insight import Insight
from app.routers.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter()

class InsightOut(BaseModel):
    id: int
    insight_type: str
    severity: str
    message_fr: str
    rule_id: Optional[str]
    is_read: bool
    generated_at: datetime
    class Config:
        from_attributes = True

@router.get("/", response_model=List[InsightOut])
def get_insights(account_id: int, unread_only: bool = False, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Insight).filter(Insight.account_id == account_id)
    if unread_only:
        q = q.filter(Insight.is_read == False)
    return q.order_by(Insight.generated_at.desc()).all()

@router.patch("/{id}/read")
def mark_read(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    insight = db.query(Insight).filter(Insight.id == id).first()
    if insight:
        insight.is_read = True
        db.commit()
    return {"ok": True}

@router.post("/generate")
def generate(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"generated": 0}
