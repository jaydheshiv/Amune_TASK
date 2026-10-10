"""Transaction API routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import (
    CategorySummary,
    ReclassifyRequest,
    TransactionCreate,
    TransactionOut,
)
from backend.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_transaction",
    summary="Create a new transaction",
)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
) -> TransactionOut:
    """Create a new income or expense transaction."""
    tx = transaction_service.create_transaction(db, data)
    return TransactionOut.model_validate(tx)


@router.get(
    "/",
    response_model=list[TransactionOut],
    status_code=status.HTTP_200_OK,
    operation_id="list_transactions",
    summary="List all transactions",
)
def list_transactions(
    month: str | None = Query(None, description="Filter by month (YYYY-MM)"),
    transaction_type: str | None = Query(None, alias="type", description="Filter by type (income or expense)"),
    category: str | None = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
) -> list[TransactionOut]:
    """Retrieve transactions with optional filtering."""
    txs = transaction_service.list_transactions(
        db,
        month=month,
        transaction_type=transaction_type,
        category=category,
    )
    return [TransactionOut.model_validate(tx) for tx in txs]


@router.get(
    "/summary",
    response_model=list[CategorySummary],
    status_code=status.HTTP_200_OK,
    operation_id="get_summary",
    summary="Get monthly summary",
)
def get_summary(
    month: str | None = Query(None, description="Filter by month (YYYY-MM)"),
    db: Session = Depends(get_db),
) -> list[CategorySummary]:
    """Retrieve monthly category aggregates with income and expense totals."""
    return transaction_service.get_summary(db, month=month)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_transaction",
    summary="Delete a transaction",
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a transaction by its ID."""
    transaction_service.delete_transaction(db, transaction_id=transaction_id)


@router.patch(
    "/{transaction_id}/reclassify",
    response_model=TransactionOut,
    status_code=status.HTTP_200_OK,
    operation_id="reclassify_transaction",
    summary="Reclassify transaction category",
)
def reclassify_transaction(
    transaction_id: int,
    data: ReclassifyRequest,
    db: Session = Depends(get_db),
) -> TransactionOut:
    """Manually update the category of a transaction, overriding auto-tagging."""
    tx = transaction_service.reclassify_transaction(
        db,
        transaction_id=transaction_id,
        new_category=data.category,
    )
    return TransactionOut.model_validate(tx)
