import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, Numeric, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class TransactionChannel(str, enum.Enum):
    ATM = "ATM"
    ONLINE = "ONLINE"
    VIREMENT = "VIREMENT"
    MANDAT = "MANDAT"
    CIB = "CIB"
    BARIDIMOB = "BARIDIMOB"
    CASH = "CASH"

class TransactionStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    amount_da: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    channel: Mapped[TransactionChannel] = mapped_column(Enum(TransactionChannel), default=TransactionChannel.ONLINE)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship(back_populates="transactions")
