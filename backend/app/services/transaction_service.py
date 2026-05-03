from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.account import Account
from app.models.transaction import Transaction

def validate_transaction(transaction_data, account, db):
    if transaction_data.type == "DEBIT":
        if account.account_type in ["CCP", "EPARGNE"]:
            if account.balance_da < transaction_data.amount_da:
                raise HTTPException(422, detail="Solde insuffisant. Votre compte CCP ne peut pas être à découvert.")

    if transaction_data.channel == "ATM" and transaction_data.type == "DEBIT":
        if transaction_data.amount_da % 1000 != 0:
            raise HTTPException(422, detail="Les retraits DAB doivent être des multiples de 1 000 DA.")

    if transaction_data.channel == "BARIDIMOB" and transaction_data.type == "DEBIT":
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_baridimob = db.query(func.sum(Transaction.amount_da)).filter(
            Transaction.account_id == account.id,
            Transaction.channel == "BARIDIMOB",
            Transaction.type == "DEBIT",
            Transaction.executed_at >= month_start
        ).scalar() or 0
        if monthly_baridimob + transaction_data.amount_da > 50000:
            raise HTTPException(422, detail=f"Plafond Baridimob atteint (50 000 DA/mois). Vous avez déjà utilisé {monthly_baridimob:,.0f} DA ce mois.")

    if transaction_data.channel == "VIREMENT":
        transaction_data.status = "PENDING"

    return transaction_data

def apply_balance_change(account, transaction, db):
    if transaction.type == "CREDIT" and transaction.status == "COMPLETED":
        account.balance_da += transaction.amount_da
    elif transaction.type == "DEBIT" and transaction.status == "COMPLETED":
        account.balance_da -= transaction.amount_da
    db.add(account)
    db.commit()
