import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.prediction import Prediction
from app.models.account import Account
import logging

logger = logging.getLogger(__name__)

def train_and_predict(account_id: int, db: Session):
    """
    Predict monthly expense and balance for the next 6 months.
    """
    # 1. Fetch transaction history
    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id, Transaction.status == TransactionStatus.COMPLETED)
        .order_by(Transaction.executed_at.asc())
        .all()
    )

    if not transactions:
        return []

    data = []
    for tx in transactions:
        amount = float(tx.amount_da) if tx.type == TransactionType.CREDIT else -float(tx.amount_da)
        data.append({
            "month": tx.executed_at.strftime("%Y-%m"),
            "amount": amount,
            "is_expense": tx.type == TransactionType.DEBIT
        })
    
    df = pd.DataFrame(data)
    if df.empty:
        return []

    # Monthly aggregation
    monthly_stats = df.groupby("month").agg(
        total_diff=("amount", "sum"),
        total_expenses=("amount", lambda x: abs(x[df.loc[x.index, "is_expense"]].sum()))
    ).reset_index()

    # Cumulative balance
    monthly_stats["balance"] = monthly_stats["total_diff"].cumsum()
    
    # 2. Linear Regression for Balance
    monthly_stats["month_index"] = range(len(monthly_stats))
    
    if len(monthly_stats) < 2:
        return []

    X = monthly_stats[["month_index"]].values
    y_balance = monthly_stats["balance"].values
    y_expenses = monthly_stats["total_expenses"].values

    model_balance = LinearRegression()
    model_balance.fit(X, y_balance)
    
    model_expenses = LinearRegression()
    model_expenses.fit(X, y_expenses)
    
    # 3. Predict next 6 months
    last_index = monthly_stats["month_index"].max()
    future_indices = np.array([[last_index + i] for i in range(1, 7)])
    
    pred_balances = model_balance.predict(future_indices)
    pred_expenses = model_expenses.predict(future_indices)
    
    # 4. Save to database
    db.query(Prediction).filter(Prediction.account_id == account_id).delete()
    
    results = []
    last_month_str = monthly_stats["month"].max()
    last_month_dt = datetime.strptime(last_month_str, "%Y-%m")
    
    for i in range(6):
        target_month_dt = (last_month_dt + timedelta(days=32 * (i + 1))).replace(day=1)
        target_month_str = target_month_dt.strftime("%Y-%m")
        
        new_pred = Prediction(
            account_id=account_id,
            predicted_for_month=target_month_str,
            predicted_expense_da=float(max(0, pred_expenses[i])),
            predicted_balance_da=float(pred_balances[i]),
            confidence_interval_da=float(pred_expenses[i] * 0.1), # 10% interval
            model_version="linear_v1"
        )
        db.add(new_pred)
        results.append(new_pred)
    
    db.commit()
    return results

def retrain_all(db: Session):
    accounts = db.query(Account).all()
    for acc in accounts:
        try:
            train_and_predict(acc.id, db)
        except Exception as e:
            logger.error(f"Failed to train account {acc.id}: {e}")
