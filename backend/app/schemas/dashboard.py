from pydantic import BaseModel
from typing import List, Optional

class DashboardSummary(BaseModel):
    balance_da: float
    income_da: float
    expense_da: float
    savings_da: float
    savings_rate_pct: float
    transaction_count: int

class CategoryStat(BaseModel):
    category_name_fr: str
    total_da: float
    percentage: float
    color_hex: str
    icon_slug: str

class MonthlyStat(BaseModel):
    month: str
    income_da: float
    expense_da: float
    savings_da: float
