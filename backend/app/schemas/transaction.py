from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from app.models.transaction import TransactionType, TransactionChannel, TransactionStatus

class CategoryBase(BaseModel):
    id: int
    name_fr: str
    icon_slug: str

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    account_id: int
    amount_da: Decimal
    type: TransactionType
    label: str
    channel: TransactionChannel
    category_id: Optional[int] = None
    notes: Optional[str] = ""
    executed_at: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: int
    amount_da: Decimal
    type: TransactionType
    label: str
    category: Optional[CategoryBase]
    channel: TransactionChannel
    status: TransactionStatus
    executed_at: datetime
    auto_categorized: Optional[bool] = False

    class Config:
        from_attributes = True
