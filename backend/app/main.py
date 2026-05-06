from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base

from app.routers import auth, accounts, transactions, categories, dashboard, insights, predictions, budgets

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinSight DZ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,         prefix="/api/v1/auth",        tags=["auth"])
app.include_router(accounts.router,     prefix="/api/v1/accounts",     tags=["accounts"])
app.include_router(transactions.router, prefix="/api/v1/transactions",  tags=["transactions"])
app.include_router(dashboard.router,    prefix="/api/v1/dashboard",     tags=["dashboard"])
app.include_router(insights.router,     prefix="/api/v1/insights",      tags=["insights"])
app.include_router(predictions.router,  prefix="/api/v1/predictions",   tags=["predictions"])
app.include_router(budgets.router,      prefix="/api/v1/budgets",       tags=["budgets"])
app.include_router(categories.router,   prefix="/api/v1/categories",    tags=["categories"])
from app.services.scheduler import start, shutdown

@app.on_event("startup")
async def startup_event():
    start()

@app.on_event("shutdown")
async def shutdown_event():
    shutdown()

@app.get("/health")
def health(): return {"status": "ok", "app": "FinSight DZ"}
