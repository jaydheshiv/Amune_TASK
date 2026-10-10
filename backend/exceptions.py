"""Custom exceptions and exception handlers."""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class DuplicateTransactionError(Exception):
    """Raised when a duplicate transaction is detected within the time window."""

    def __init__(self, detail: str = "Duplicate transaction detected within the time window."):
        self.detail = detail
        super().__init__(detail)


class TransactionNotFoundError(Exception):
    """Raised when a requested transaction is not found."""

    def __init__(self, detail: str = "Transaction not found."):
        self.detail = detail
        super().__init__(detail)


class InvalidTransactionError(Exception):
    """Raised when transaction data violates business rules or semantic validation."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


async def duplicate_transaction_handler(request: Request, exc: DuplicateTransactionError) -> JSONResponse:
    """Handle DuplicateTransactionError with 409 status code."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail},
    )


async def transaction_not_found_handler(request: Request, exc: TransactionNotFoundError) -> JSONResponse:
    """Handle TransactionNotFoundError with 404 status code."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


async def invalid_transaction_handler(request: Request, exc: InvalidTransactionError) -> JSONResponse:
    """Handle InvalidTransactionError with 422 status code."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.detail},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions with safe 500 status code without leaking traces."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
