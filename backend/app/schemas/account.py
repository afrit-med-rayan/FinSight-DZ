from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

class AccountResponse(BaseModel):
    id: int
    rib: str
    account_type: str
    balance_da: Decimal
    currency: str
    is_active: bool

    class Config:
        from_attributes = True
