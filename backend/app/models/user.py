from datetime import datetime
from typing import List
from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    wilaya_code: Mapped[int] = mapped_column(Integer, default=16)  # 16 = Alger
    salary_day: Mapped[int] = mapped_column(Integer, default=20)   # day of month salary arrives
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    accounts: Mapped[List["Account"]] = relationship(back_populates="user")
