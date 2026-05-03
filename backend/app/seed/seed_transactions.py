import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction
from app.models.account import Account

MONTHLY_TEMPLATE = {
    "salary": {"amount_range": (55000, 65000), "type": "CREDIT", "category_id": 2, "label": "SALAIRE MENSUEL - VIREMENT", "channel": "VIREMENT", "day": "salary_day"},
    "loyer":    {"amount": 32000,  "type": "DEBIT", "category_id": 21, "label": "LOYER MENSUEL", "channel": "VIREMENT", "day": 3},
    "sonelgaz": {"amount_range": (2800, 4200), "type": "DEBIT", "category_id": 22, "label": "SONELGAZ PAIEMENT", "channel": "ONLINE", "day": 10},
    "ade_eau":  {"amount_range": (600, 1200),  "type": "DEBIT", "category_id": 23, "label": "ADE - FACTURE EAU", "channel": "ONLINE", "day": 12},
    "telecom":  {"amount": 1500, "type": "DEBIT", "category_id": 43, "label": "OOREDOO RECHARGE", "channel": "BARIDIMOB", "day": 5},
    "epicerie":   {"amount_range": (3000, 6000),  "type": "DEBIT", "category_id": 11, "label": "MARCHE / EPICERIE", "channel": "CASH", "weekly": True},
    "transport":  {"amount_range": (500, 2500),   "type": "DEBIT", "category_id": 31, "label": "TAXI / TRANSPORT", "channel": "CIB", "weekly": True},
    "restaurant": {"amount_range": (1500, 4000),  "type": "DEBIT", "category_id": 13, "label": "RESTAURANT", "channel": "CIB", "weekly": True},
    "pharmacie":  {"amount_range": (0, 3000),     "type": "DEBIT", "category_id": 51, "label": "PHARMACIE", "channel": "CASH", "monthly": True, "probability": 0.6},
}

def generate_demo_data(account_id: int, user_salary_day: int, db: Session):
    start_date = datetime.now() - relativedelta(months=12)
    end_date = datetime.now()
    
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        month = current_date.month
        year = current_date.year
        
        is_ramadan = (year == 2024 and month == 3) or (year == 2025 and month == 3) or (year == 2026 and month == 2)
        is_eid = (year == 2024 and month == 6) or (year == 2025 and month == 6) or (year == 2026 and month == 6)
        
        for key, template in MONTHLY_TEMPLATE.items():
            if template.get("weekly"):
                for week in range(4):
                    amount = random.uniform(*template["amount_range"])
                    if key in ["epicerie", "restaurant"] and is_ramadan:
                        amount *= 1.35
                    day = random.randint(1 + week*7, 7 + week*7)
                    if day > 28: day = 28
                    exec_date = current_date.replace(day=day)
                    if exec_date > end_date: continue
                    txn = Transaction(
                        account_id=account_id,
                        amount_da=amount,
                        type=template["type"],
                        category_id=template["category_id"],
                        label=template["label"],
                        channel=template["channel"],
                        status="COMPLETED",
                        executed_at=exec_date,
                        created_at=exec_date
                    )
                    db.add(txn)
            else:
                prob = template.get("probability", 1.0)
                if random.random() <= prob:
                    if "amount" in template:
                        amount = template["amount"]
                    else:
                        amount = random.uniform(*template["amount_range"])
                    
                    if key == "salary":
                        day = user_salary_day
                    else:
                        day = template.get("day", random.randint(1, 28))
                    
                    if day > 28: day = 28
                    exec_date = current_date.replace(day=day)
                    if exec_date > end_date: continue
                    
                    txn = Transaction(
                        account_id=account_id,
                        amount_da=amount,
                        type=template["type"],
                        category_id=template["category_id"],
                        label=template["label"],
                        channel=template["channel"],
                        status="COMPLETED",
                        executed_at=exec_date,
                        created_at=exec_date
                    )
                    db.add(txn)
                    
        if month == 12:
            exec_date = current_date.replace(day=15)
            if exec_date <= end_date:
                txn = Transaction(
                    account_id=account_id, amount_da=60000, type="CREDIT", category_id=3,
                    label="PRIME DE FIN D'ANNEE", channel="VIREMENT", status="COMPLETED",
                    executed_at=exec_date, created_at=exec_date
                )
                db.add(txn)
        if is_eid:
            exec_date = current_date.replace(day=10)
            if exec_date <= end_date:
                txn = Transaction(
                    account_id=account_id, amount_da=25000, type="DEBIT", category_id=91,
                    label="ACHAT MOUTON AID", channel="CASH", status="COMPLETED",
                    executed_at=exec_date, created_at=exec_date
                )
                db.add(txn)

        current_date += relativedelta(months=1)
        
    db.commit()
    
    balance = db.query(func.sum(Transaction.amount_da)).filter(Transaction.account_id == account_id, Transaction.type == "CREDIT", Transaction.status == "COMPLETED").scalar() or 0
    expense = db.query(func.sum(Transaction.amount_da)).filter(Transaction.account_id == account_id, Transaction.type == "DEBIT", Transaction.status == "COMPLETED").scalar() or 0
    account = db.query(Account).filter(Account.id == account_id).first()
    if account:
        account.balance_da = balance - expense
        db.add(account)
        db.commit()
