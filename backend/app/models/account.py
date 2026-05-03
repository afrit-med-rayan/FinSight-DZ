import enum
from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import Integer, String, Boolean, DateTime, Numeric, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class AccountType(str, enum.Enum):
    CCP = "CCP"
    EPARGNE = "EPARGNE"
    CPA = "CPA"
    BUSINESS = "BUSINESS"

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rib: Mapped[str] = mapped_column(String(25), unique=True)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), default=AccountType.CCP)
    balance_da: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="DZD")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="account")
