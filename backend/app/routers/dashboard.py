from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.category import Category
from app.routers.auth import get_current_user
from app.schemas.dashboard import DashboardSummary, CategoryStat, MonthlyStat

router = APIRouter()

CATEGORY_COLORS = ["#185FA5","#0F6E56","#BA7517","#A32D2D","#534AB7","#993556","#3B6D11","#5F5E5A"]

def _get_account(account_id: int, user: User, db: Session):
    return db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()

@router.get("/summary", response_model=DashboardSummary)
def get_summary(account_id: int, month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    year, mo = int(month.split("-")[0]), int(month.split("-")[1])
    account = _get_account(account_id, current_user, db)

    base = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.status == "COMPLETED",
        extract("year", Transaction.executed_at) == year,
        extract("month", Transaction.executed_at) == mo,
    )

    income = float(base.filter(Transaction.type == "CREDIT").with_entities(func.sum(Transaction.amount_da)).scalar() or 0)
    expense = float(base.filter(Transaction.type == "DEBIT").with_entities(func.sum(Transaction.amount_da)).scalar() or 0)
    count = base.count()
    savings = max(0, income - expense)
    rate = round((savings / income * 100), 1) if income > 0 else 0.0
    balance = float(account.balance_da) if account else 0.0

    return DashboardSummary(
        balance_da=balance, income_da=income, expense_da=expense,
        savings_da=savings, savings_rate_pct=rate, transaction_count=count
    )

@router.get("/charts/categories", response_model=List[CategoryStat])
def get_category_chart(account_id: int, month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    year, mo = int(month.split("-")[0]), int(month.split("-")[1])

    results = db.query(
        Category.name_fr, Category.icon_slug, func.sum(Transaction.amount_da).label("total")
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        Transaction.account_id == account_id,
        Transaction.type == "DEBIT",
        Transaction.status == "COMPLETED",
        extract("year", Transaction.executed_at) == year,
        extract("month", Transaction.executed_at) == mo,
    ).group_by(Category.name_fr, Category.icon_slug).order_by(func.sum(Transaction.amount_da).desc()).all()

    grand_total = sum(float(r.total) for r in results) or 1

    return [
        CategoryStat(
            category_name_fr=r.name_fr,
            total_da=float(r.total),
            percentage=round(float(r.total) / grand_total * 100, 1),
            color_hex=CATEGORY_COLORS[i % len(CATEGORY_COLORS)],
            icon_slug=r.icon_slug,
        )
        for i, r in enumerate(results)
    ]

@router.get("/charts/monthly", response_model=List[MonthlyStat])
def get_monthly_chart(account_id: int, months: int = 12, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(
        extract("year", Transaction.executed_at).label("year"),
        extract("month", Transaction.executed_at).label("month"),
        Transaction.type,
        func.sum(Transaction.amount_da).label("total"),
    ).filter(
        Transaction.account_id == account_id,
        Transaction.status == "COMPLETED",
    ).group_by("year", "month", Transaction.type).order_by("year", "month").all()

    monthly = {}
    for r in results:
        key = f"{int(r.year)}-{int(r.month):02d}"
        if key not in monthly:
            monthly[key] = {"income_da": 0.0, "expense_da": 0.0}
        if r.type == "CREDIT":
            monthly[key]["income_da"] = float(r.total)
        else:
            monthly[key]["expense_da"] = float(r.total)

    output = []
    for month_key in sorted(monthly.keys())[-months:]:
        d = monthly[month_key]
        output.append(MonthlyStat(
            month=month_key,
            income_da=d["income_da"],
            expense_da=d["expense_da"],
            savings_da=max(0, d["income_da"] - d["expense_da"]),
        ))
    return output

@router.get("/charts/weekly")
def get_weekly_chart(account_id: int, month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"week_label": "Sem. 1", "categories": []}, {"week_label": "Sem. 2", "categories": []}, {"week_label": "Sem. 3", "categories": []}, {"week_label": "Sem. 4", "categories": []}]
