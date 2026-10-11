"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.exceptions import (
    DuplicateTransactionError,
    InvalidTransactionError,
    TransactionNotFoundError,
    duplicate_transaction_handler,
    generic_exception_handler,
    invalid_transaction_handler,
    transaction_not_found_handler,
)
from backend.routers import transactions

app = FastAPI(
    title="Personal Finance Tracker API",
    version="1.0.0",
    description="API for tracking income and expenses, auto-categorizing transactions, and financial summaries.",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(DuplicateTransactionError, duplicate_transaction_handler)
app.add_exception_handler(TransactionNotFoundError, transaction_not_found_handler)
app.add_exception_handler(InvalidTransactionError, invalid_transaction_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(transactions.router)


@app.get("/", tags=["system"], operation_id="root_index")
def root_index() -> dict[str, str]:
    """Root endpoint confirming backend status and providing links."""
    return {
        "status": "running",
        "message": "Personal Finance Tracker API is running",
        "docs": "/docs",
        "health": "/health",
        "frontend": "http://localhost:3000",
    }


@app.get("/health", tags=["system"], operation_id="health_check")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
