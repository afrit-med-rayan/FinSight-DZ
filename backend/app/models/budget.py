import enum
from datetime import date
from decimal import Decimal
from sqlalchemy import Integer, Numeric, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class PeriodType(str, enum.Enum):
    MENSUEL = "MENSUEL"
    HEBDOMADAIRE = "HEBDOMADAIRE"
    RAMADAN = "RAMADAN"

class Budget(Base):
    __tablename__ = "budgets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    limit_da: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    period_type: Mapped[PeriodType] = mapped_column(Enum(PeriodType), default=PeriodType.MENSUEL)
    start_date: Mapped[date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
