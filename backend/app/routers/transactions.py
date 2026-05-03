from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.routers.auth import get_current_user
from app.services.transaction_service import validate_transaction, apply_balance_change
from app.services.categorizer import auto_categorize

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
def create_transaction(txn_in: TransactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == txn_in.account_id, Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    txn_in = validate_transaction(txn_in, account, db)
    
    auto_cat = False
    if not txn_in.category_id:
        txn_in.category_id = auto_categorize(txn_in.label)
        auto_cat = True

    txn = Transaction(
        account_id=txn_in.account_id,
        amount_da=txn_in.amount_da,
        type=txn_in.type,
        category_id=txn_in.category_id,
        label=txn_in.label,
        channel=txn_in.channel,
        notes=txn_in.notes,
        executed_at=txn_in.executed_at or func.now(),
        status="COMPLETED" if txn_in.channel != "VIREMENT" else "PENDING"
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    apply_balance_change(account, txn, db)
    txn.auto_categorized = auto_cat
    return txn

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    account_id: int,
    month: Optional[str] = None,
    category_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    query = db.query(Transaction).filter(Transaction.account_id == account_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    return query.order_by(desc(Transaction.executed_at)).limit(100).all()

@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txn = db.query(Transaction).join(Account).filter(Transaction.id == id, Account.user_id == current_user.id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return txn
