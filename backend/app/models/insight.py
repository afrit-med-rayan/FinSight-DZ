import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class InsightSeverity(str, enum.Enum):
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"
    GOOD = "GOOD"
    CONTEXT = "CONTEXT"

class Insight(Base):
    __tablename__ = "insights"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    insight_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[InsightSeverity] = mapped_column(Enum(InsightSeverity))
    message_fr: Mapped[str] = mapped_column(Text)
    message_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rule_id: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
