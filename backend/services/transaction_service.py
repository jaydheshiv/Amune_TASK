from datetime import datetime, timedelta, timezone
import re
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from backend.config import DUPLICATE_WINDOW_SECONDS
from backend.exceptions import (
    DuplicateTransactionError,
    InvalidTransactionError,
    TransactionNotFoundError,
)
from backend.models import Transaction
from backend.schemas import CategorySummary, TransactionCreate
from backend.services.categorizer import (
    categorize,
    check_semantic_type_conflict,
    normalize_text,
)

MONTH_REGEX = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def get_utc_now() -> datetime:
    """Return current naive UTC timestamp for SQLite storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
    """Create a new transaction enforcing semantic rules, sign convention, and duplicate detection."""
    # 1. Semantic validation (e.g. Rent as income, Salary as expense)
    conflict = check_semantic_type_conflict(data.description, data.transaction_type)
    if conflict:
        raise InvalidTransactionError(conflict)

    # 2. Sign handling: expenses stored negative, income stored positive
    stored_amount = -abs(data.amount) if data.transaction_type == "expense" else abs(data.amount)

    # 3. Duplicate check within time window
    now = get_utc_now()
    window_start = now - timedelta(seconds=DUPLICATE_WINDOW_SECONDS)

    recent_candidates = (
        db.query(Transaction)
        .filter(
            Transaction.timestamp >= window_start,
            Transaction.transaction_type == data.transaction_type,
        )
        .all()
    )

    norm_new_desc = normalize_text(data.description)
    for cand in recent_candidates:
        if (
            normalize_text(cand.description) == norm_new_desc
            and abs(cand.amount - stored_amount) < 1e-4
        ):
            raise DuplicateTransactionError(
                f"Duplicate transaction detected within {DUPLICATE_WINDOW_SECONDS} seconds."
            )

    # 4. Auto-categorize
    category = categorize(data.description)

    # 5. Save to database
    db_transaction = Transaction(
        description=data.description.strip(),
        amount=stored_amount,
        transaction_type=data.transaction_type,
        category=category,
        auto_tagged=True,
        timestamp=now,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def list_transactions(
    db: Session,
    month: str | None = None,
    transaction_type: str | None = None,
    category: str | None = None,
) -> list[Transaction]:
    """Retrieve all transactions with optional filtering by month, type, and category."""
    query = db.query(Transaction)

    if month is not None:
        if not MONTH_REGEX.match(month):
            raise InvalidTransactionError("Invalid month format. Expected YYYY-MM.")
        query = query.filter(func.strftime("%Y-%m", Transaction.timestamp) == month)

    if transaction_type is not None:
        if transaction_type not in ("income", "expense"):
            raise InvalidTransactionError("Invalid transaction type. Expected 'income' or 'expense'.")
        query = query.filter(Transaction.transaction_type == transaction_type)

    if category is not None:
        clean_category = category.strip().lower()
        query = query.filter(func.lower(Transaction.category) == clean_category)

    return query.order_by(Transaction.timestamp.desc(), Transaction.id.desc()).all()


def get_summary(db: Session, month: str | None = None) -> list[CategorySummary]:
    """Compute monthly income and expense summary grouped by month and category."""
    if month is not None:
        if not MONTH_REGEX.match(month):
            raise InvalidTransactionError("Invalid month format. Expected YYYY-MM.")

    month_col = func.strftime("%Y-%m", Transaction.timestamp).label("month")
    cat_col = func.coalesce(Transaction.category, "Uncategorized").label("category")

    income_expr = func.coalesce(
        func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0.0)),
        0.0,
    ).label("total_income")

    expense_expr = func.coalesce(
        func.sum(case((Transaction.amount < 0, -Transaction.amount), else_=0.0)),
        0.0,
    ).label("total_expense")

    query = db.query(month_col, cat_col, income_expr, expense_expr)

    if month is not None:
        query = query.filter(func.strftime("%Y-%m", Transaction.timestamp) == month)

    rows = (
        query.group_by(month_col, cat_col)
        .order_by(month_col.desc(), cat_col.asc())
        .all()
    )

    return [
        CategorySummary(
            month=r.month,
            category=r.category,
            total_income=float(round(r.total_income, 2)),
            total_expense=float(round(r.total_expense, 2)),
        )
        for r in rows
    ]


def delete_transaction(db: Session, transaction_id: int) -> None:
    """Delete a transaction by ID or raise TransactionNotFoundError."""
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise TransactionNotFoundError(f"Transaction with id {transaction_id} not found.")

    db.delete(tx)
    db.commit()


def reclassify_transaction(db: Session, transaction_id: int, new_category: str) -> Transaction:
    """Manually reclassify a transaction category and set auto_tagged to False."""
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise TransactionNotFoundError(f"Transaction with id {transaction_id} not found.")

    tx.category = new_category.strip()
    tx.auto_tagged = False

    db.commit()
    db.refresh(tx)
    return tx
