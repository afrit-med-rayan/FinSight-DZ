"""
Insight Engine — generates AI-powered financial insights for FinSight DZ.
Implements rules R-01 through R-09 as specified.
"""
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.account import Account
from app.models.insight import Insight, InsightSeverity
from app.models.transaction import Transaction, TransactionType, TransactionStatus

# ---------------------------------------------------------------------------
# Cost-of-living benchmarks for Alger (DA)
# ---------------------------------------------------------------------------
BENCHMARKS_DA = {
    "alimentation": {"low": 12000, "median": 22000, "high": 40000},
    "loyer":        {"low": 20000, "median": 35000, "high": 60000},
    "transport":    {"low": 3000,  "median": 7000,  "high": 15000},
    "telecom":      {"low": 1500,  "median": 3000,  "high": 6000},
    "sante":        {"low": 1000,  "median": 3500,  "high": 10000},
}
SAVINGS_RATE_TARGET = 0.10  # 10 % minimum

# Category ID groupings (from seed_categories)
ALIMENTATION_IDS = {10, 11, 12, 13, 14}
TRANSPORT_IDS    = {30, 31, 32, 33, 34}
TELECOM_IDS      = {40, 41, 42, 43}
SANTE_IDS        = {50, 51, 52, 53}
LOYER_IDS        = {20, 21, 22, 23, 24}
FETES_IDS        = {90, 91, 92, 93}     # excluded from anomaly detection

# ---------------------------------------------------------------------------
# Ramadan date approximations (year → (start_month, start_day, end_month, end_day))
# ---------------------------------------------------------------------------
RAMADAN_PERIODS = {
    2024: (3, 11, 4, 9),
    2025: (3, 1, 3, 29),
    2026: (2, 18, 3, 19),
}


def _is_ramadan(dt: datetime) -> bool:
    """Return True if the given datetime falls inside Ramadan."""
    year = dt.year
    period = RAMADAN_PERIODS.get(year)
    if not period:
        return False
    sm, sd, em, ed = period
    start = datetime(year, sm, sd)
    end   = datetime(year, em, ed, 23, 59, 59)
    return start <= dt <= end


def _month_bounds(year: int, month: int):
    """Return (start_datetime, end_datetime) for the given year/month."""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end


def _sum_debits(account_id: int, category_ids: set, start: datetime, end: datetime, db: Session) -> float:
    result = db.query(func.sum(Transaction.amount_da)).filter(
        Transaction.account_id == account_id,
        Transaction.type == TransactionType.DEBIT,
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.category_id.in_(category_ids),
        Transaction.executed_at >= start,
        Transaction.executed_at < end,
    ).scalar()
    return float(result or 0)


def _total_income(account_id: int, start: datetime, end: datetime, db: Session) -> float:
    result = db.query(func.sum(Transaction.amount_da)).filter(
        Transaction.account_id == account_id,
        Transaction.type == TransactionType.CREDIT,
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.executed_at >= start,
        Transaction.executed_at < end,
    ).scalar()
    return float(result or 0)


def _total_expense(account_id: int, start: datetime, end: datetime, db: Session) -> float:
    result = db.query(func.sum(Transaction.amount_da)).filter(
        Transaction.account_id == account_id,
        Transaction.type == TransactionType.DEBIT,
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.executed_at >= start,
        Transaction.executed_at < end,
    ).scalar()
    return float(result or 0)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def generate_insights(account_id: int, db: Session) -> List[Insight]:
    """
    Generate insights for account_id.
    Deletes existing unread insights first, then runs all 9 rules.
    Returns the list of newly created Insight objects.
    """
    # Delete old unread insights so we get a fresh set
    db.query(Insight).filter(
        Insight.account_id == account_id,
        Insight.is_read == False,
    ).delete(synchronize_session=False)
    db.commit()

    now = datetime.utcnow()
    year, month = now.year, now.month
    month_start, month_end = _month_bounds(year, month)

    # Previous month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    prev_start, prev_end = _month_bounds(prev_year, prev_month)

    insights: List[Insight] = []

    def _save(insight_type: str, severity: InsightSeverity, message_fr: str, rule_id: str):
        ins = Insight(
            account_id=account_id,
            insight_type=insight_type,
            severity=severity,
            message_fr=message_fr,
            rule_id=rule_id,
        )
        db.add(ins)
        insights.append(ins)

    # --- R-08: Ramadan suppressor (run first to flag suppression) ---
    is_ramadan_month = _is_ramadan(now)
    if is_ramadan_month:
        _save(
            "RAMADAN_CONTEXT",
            InsightSeverity.CONTEXT,
            "Le mois de Ramadan est détecté. Les hausses des dépenses alimentaires sont normales "
            "et ne génèrent pas d'alertes ce mois.",
            "R-08",
        )

    # Compute this month figures
    income_da  = _total_income(account_id, month_start, month_end, db)
    expense_da = _total_expense(account_id, month_start, month_end, db)

    # Category spending this month
    alim_spend  = _sum_debits(account_id, ALIMENTATION_IDS, month_start, month_end, db)
    transport_spend = _sum_debits(account_id, TRANSPORT_IDS, month_start, month_end, db)
    telecom_spend   = _sum_debits(account_id, TELECOM_IDS,   month_start, month_end, db)

    # --- R-01: Category overspend vs benchmark ---
    benchmark_checks = [
        ("alimentation", alim_spend,      not is_ramadan_month),
        ("transport",    transport_spend,  True),
        ("telecom",      telecom_spend,    True),
    ]
    cat_labels = {
        "alimentation": "Alimentation",
        "transport":    "Transport",
        "telecom":      "Télécommunications",
    }
    for key, spend, run_check in benchmark_checks:
        if not run_check:
            continue
        bench_high = BENCHMARKS_DA[key]["high"]
        if spend > bench_high:
            diff = spend - bench_high
            _save(
                "CATEGORY_OVERSPEND",
                InsightSeverity.WARN,
                (
                    f"Vos dépenses {cat_labels[key]} ce mois ({spend:,.0f} DA) dépassent le seuil élevé "
                    f"pour Alger ({bench_high:,.0f} DA). Vous pourriez économiser {diff:,.0f} DA en réduisant "
                    "ces dépenses."
                ),
                "R-01",
            )

    # --- R-02: Spending > 85 % of income ---
    if income_da > 0 and expense_da / income_da > 0.85:
        pct = round(expense_da / income_da * 100)
        target = round(income_da * SAVINGS_RATE_TARGET)
        _save(
            "HIGH_EXPENSE_RATIO",
            InsightSeverity.WARN,
            (
                f"Vous dépensez {pct}% de vos revenus ce mois. Il est recommandé d'épargner au moins 10%. "
                f"Avec votre salaire, cela représente {target:,.0f} DA/mois."
            ),
            "R-02",
        )

    # --- R-03: No income detected by the 25th ---
    if now.day > 25:
        salary_this_month = db.query(func.sum(Transaction.amount_da)).filter(
            Transaction.account_id == account_id,
            Transaction.type == TransactionType.CREDIT,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.executed_at >= month_start,
            Transaction.executed_at < month_end,
            Transaction.label.ilike("%SALAIRE%"),
        ).scalar()
        if not salary_this_month:
            _save(
                "NO_INCOME_DETECTED",
                InsightSeverity.INFO,
                "Aucun salaire détecté ce mois avant le 25. Vérifiez votre compte ou signalez un problème.",
                "R-03",
            )

    # --- R-04: Low balance alert ---
    account = db.query(Account).filter(Account.id == account_id).first()
    if account and float(account.balance_da) < 5000:
        cutoff_48h = now - timedelta(hours=48)
        recent_debit = db.query(Transaction).filter(
            Transaction.account_id == account_id,
            Transaction.type == TransactionType.DEBIT,
            Transaction.executed_at >= cutoff_48h,
        ).first()
        if recent_debit:
            _save(
                "LOW_BALANCE",
                InsightSeverity.CRITICAL,
                (
                    f"Votre solde est très bas ({float(account.balance_da):,.0f} DA). "
                    "Évitez les dépenses non essentielles pour tenir jusqu'à la fin du mois."
                ),
                "R-04",
            )

    # --- R-05: Unusually large single transaction ---
    three_months_ago = now - timedelta(days=90)
    avg_result = db.query(func.avg(Transaction.amount_da)).filter(
        Transaction.account_id == account_id,
        Transaction.type == TransactionType.DEBIT,
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.executed_at >= three_months_ago,
        Transaction.category_id.notin_(FETES_IDS),
    ).scalar()
    avg_amount = float(avg_result or 0)

    if avg_amount > 0:
        threshold = avg_amount * 3
        large_txns = db.query(Transaction).filter(
            Transaction.account_id == account_id,
            Transaction.type == TransactionType.DEBIT,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.executed_at >= month_start,
            Transaction.executed_at < month_end,
            Transaction.amount_da > threshold,
            Transaction.category_id.notin_(FETES_IDS),
        ).all()
        for txn in large_txns:
            mult = round(float(txn.amount_da) / avg_amount, 1)
            _save(
                "UNUSUAL_TRANSACTION",
                InsightSeverity.INFO,
                (
                    f"Une dépense inhabituelle a été détectée : {float(txn.amount_da):,.0f} DA pour "
                    f"'{txn.label}'. Cela représente {mult}× votre montant moyen habituel."
                ),
                "R-05",
            )

    # --- R-06: Month-over-month category increase > 25 % ---
    for cat_key, cat_ids, label in [
        ("alimentation", ALIMENTATION_IDS, "Alimentation"),
        ("transport",    TRANSPORT_IDS,    "Transport"),
        ("telecom",      TELECOM_IDS,      "Télécommunications"),
    ]:
        curr_spend = _sum_debits(account_id, cat_ids, month_start, month_end, db)
        prev_spend = _sum_debits(account_id, cat_ids, prev_start, prev_end, db)
        if prev_spend > 0 and curr_spend > prev_spend * 1.25:
            pct = round((curr_spend - prev_spend) / prev_spend * 100)
            _save(
                "CATEGORY_INCREASE",
                InsightSeverity.INFO,
                (
                    f"Vos dépenses {label} ont augmenté de {pct}% par rapport au mois dernier "
                    f"({prev_spend:,.0f} DA → {curr_spend:,.0f} DA)."
                ),
                "R-06",
            )

    # --- R-07: Savings rate improved ---
    savings_da = income_da - expense_da
    if income_da > 0:
        savings_rate = savings_da / income_da

        # Compute avg savings rate over last 3 months
        rates = []
        for offset in range(1, 4):
            mo = month - offset
            yr = year
            while mo <= 0:
                mo += 12
                yr -= 1
            s, e = _month_bounds(yr, mo)
            inc = _total_income(account_id, s, e, db)
            exp = _total_expense(account_id, s, e, db)
            if inc > 0:
                rates.append((inc - exp) / inc)

        if rates:
            avg_rate = sum(rates) / len(rates)
            if savings_rate > avg_rate + 0.05:
                _save(
                    "SAVINGS_IMPROVED",
                    InsightSeverity.GOOD,
                    (
                        f"Bravo ! Votre taux d'épargne ce mois ({round(savings_rate*100)}%) est supérieur à "
                        f"votre moyenne des 3 derniers mois ({round(avg_rate*100)}%). Continuez ainsi."
                    ),
                    "R-07",
                )

    # --- R-09: December prime de fin d'année ---
    if month == 12:
        _save(
            "DECEMBER_PRIME",
            InsightSeverity.CONTEXT,
            "Décembre est souvent le mois de la prime de fin d'année. Si vous l'avez reçue, "
            "pensez à en mettre une partie de côté.",
            "R-09",
        )

    db.commit()
    return insights
