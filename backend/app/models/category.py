from typing import List, Optional
from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_fr: Mapped[str] = mapped_column(String(80))
    name_ar: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    icon_slug: Mapped[str] = mapped_column(String(50), default="tag")
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_essential: Mapped[bool] = mapped_column(Boolean, default=False)
    is_income: Mapped[bool] = mapped_column(Boolean, default=False)
    children: Mapped[List["Category"]] = relationship(back_populates="parent")
    parent: Mapped[Optional["Category"]] = relationship(back_populates="children", remote_side="Category.id")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="category")
