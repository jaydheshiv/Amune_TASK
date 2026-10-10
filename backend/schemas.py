"""Pydantic schemas for request and response validation."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""

    description: str = Field(..., min_length=1, max_length=200, description="Transaction description")
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    transaction_type: Literal["income", "expense"] = Field(
        ..., description="Type of transaction: income or expense"
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Description cannot be empty or only whitespace")
        return stripped


class TransactionOut(BaseModel):
    """Schema for returning transaction details."""

    id: int
    description: str
    amount: float
    transaction_type: Literal["income", "expense"]
    category: str | None = None
    auto_tagged: bool
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount")
    @classmethod
    def ensure_absolute_amount(cls, v: float) -> float:
        """API always returns absolute amount to the client."""
        return abs(v)


class ReclassifyRequest(BaseModel):
    """Schema for reclassifying a transaction category."""

    category: str = Field(..., min_length=1, max_length=50, description="New category name")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Category cannot be empty or only whitespace")
        return stripped


class CategorySummary(BaseModel):
    """Schema for monthly income and expense summary per category."""

    month: str = Field(..., description="Month in YYYY-MM format")
    category: str = Field(..., description="Transaction category")
    total_income: float = Field(..., ge=0, description="Total income for the category in the month")
    total_expense: float = Field(..., ge=0, description="Total expense for the category in the month")
