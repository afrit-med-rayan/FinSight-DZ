from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.insight_engine import generate_insights
from app.services.ml_predictor import retrain_all
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def daily_tasks():
    """
    Run daily: Generate new insights for all accounts.
    """
    logger.info("Running daily tasks: Generating insights...")
    db: Session = SessionLocal()
    try:
        accounts = db.query(Account).all()
        for acc in accounts:
            generate_insights(acc.id, db)
        logger.info(f"Insights generated for {len(accounts)} accounts.")
    except Exception as e:
        logger.error(f"Daily task failed: {e}")
    finally:
        db.close()

def weekly_tasks():
    """
    Run weekly: Retrain ML models for all accounts.
    """
    logger.info("Running weekly tasks: Retraining ML models...")
    db: Session = SessionLocal()
    try:
        retrain_all(db)
        logger.info("ML models retrained successfully.")
    except Exception as e:
        logger.error(f"Weekly task failed: {e}")
    finally:
        db.close()

def settle_virements():
    """
    Run daily: Settle virements that have been pending for more than 2 days.
    """
    logger.info("Running settlement tasks: Completing virements...")
    db: Session = SessionLocal()
    try:
        cutoff = datetime.now() - timedelta(days=2)
        virements = db.query(Transaction).filter(
            Transaction.channel == "VIREMENT",
            Transaction.status == "PENDING",
            Transaction.created_at <= cutoff
        ).all()
        
        for v in virements:
            v.status = "COMPLETED"
            v.executed_at = datetime.now()
            # Update account balance
            account = db.query(Account).filter(Account.id == v.account_id).first()
            if account:
                if v.type == "CREDIT":
                    account.balance_da += v.amount_da
                else:
                    account.balance_da -= v.amount_da
        
        db.commit()
        logger.info(f"Settled {len(virements)} virements.")
    except Exception as e:
        logger.error(f"Settlement task failed: {e}")
        db.rollback()
    finally:
        db.close()

# ── Schedule Jobs ──────────────────────────────────────────────────────────

# Daily at 01:00 AM
scheduler.add_job(
    daily_tasks,
    CronTrigger(hour=1, minute=0),
    id="daily_insights",
    replace_existing=True
)

# Daily at 02:00 AM
scheduler.add_job(
    settle_virements,
    CronTrigger(hour=2, minute=0),
    id="daily_settlement",
    replace_existing=True
)

# Weekly on Sunday at 03:00 AM
scheduler.add_job(
    weekly_tasks,
    CronTrigger(day_of_week="sun", hour=3, minute=0),
    id="weekly_ml_retrain",
    replace_existing=True
)

def start():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started.")

def shutdown():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")
