from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    predicted_for_month: Mapped[str] = mapped_column(String(7))
    predicted_expense_da: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    predicted_balance_da: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    confidence_interval_da: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    model_version: Mapped[str] = mapped_column(String(20), default="linear_v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
