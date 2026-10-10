"""Database models for Personal Finance Tracker."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    CheckConstraint,
    func,
)
from backend.database import Base


class Transaction(Base):
    """Transaction database model matching challenge specification."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    category = Column(String, nullable=True)
    auto_tagged = Column(Boolean, nullable=False, default=True, server_default="1")
    timestamp = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('income','expense')",
            name="ck_transaction_type",
        ),
    )
