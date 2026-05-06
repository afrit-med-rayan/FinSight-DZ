from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.insight import Insight
from app.routers.auth import get_current_user
from app.services.insight_engine import generate_insights
from pydantic import BaseModel
from datetime import datetime

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
def get_insights(
    account_id: int,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Insight).filter(Insight.account_id == account_id)
    if unread_only:
        q = q.filter(Insight.is_read == False)
    return q.order_by(Insight.generated_at.desc()).all()


@router.get("/unread-count")
def unread_count(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = (
        db.query(Insight)
        .filter(Insight.account_id == account_id, Insight.is_read == False)
        .count()
    )
    return {"count": count}


@router.patch("/{id}/read")
def mark_read(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    insight = db.query(Insight).filter(Insight.id == id).first()
    if insight:
        insight.is_read = True
        db.commit()
    return {"ok": True}


@router.patch("/mark-all-read")
def mark_all_read(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(Insight).filter(
        Insight.account_id == account_id,
        Insight.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}


@router.post("/generate")
def generate(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_insights = generate_insights(account_id, db)
    return {"generated": len(new_insights)}
