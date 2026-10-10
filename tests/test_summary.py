"""Unit tests for monthly summary aggregation endpoint."""

from datetime import datetime
from backend.models import Transaction


def test_summary_empty(client):
    res = client.get("/transactions/summary")
    assert res.status_code == 200
    assert res.json() == []


def test_summary_grouping_and_absolute_totals(client, db_session):
    # Populate test data
    db_session.add_all([
        Transaction(
            description="Salary August",
            amount=5000.00,
            transaction_type="income",
            category="Salary",
            auto_tagged=True,
            timestamp=datetime(2026, 8, 1, 9, 0, 0),
        ),
        Transaction(
            description="Freelance August",
            amount=500.00,
            transaction_type="income",
            category="Salary",
            auto_tagged=False,
            timestamp=datetime(2026, 8, 15, 9, 0, 0),
        ),
        Transaction(
            description="Rent August",
            amount=-1200.00,
            transaction_type="expense",
            category="Rent",
            auto_tagged=True,
            timestamp=datetime(2026, 8, 2, 10, 0, 0),
        ),
        Transaction(
            description="McDonalds August",
            amount=-20.00,
            transaction_type="expense",
            category="Food",
            auto_tagged=True,
            timestamp=datetime(2026, 8, 3, 12, 0, 0),
        ),
        Transaction(
            description="Pizza August",
            amount=-30.00,
            transaction_type="expense",
            category="Food",
            auto_tagged=True,
            timestamp=datetime(2026, 8, 4, 19, 0, 0),
        ),
        # September transaction
        Transaction(
            description="Salary September",
            amount=5000.00,
            transaction_type="income",
            category="Salary",
            auto_tagged=True,
            timestamp=datetime(2026, 9, 1, 9, 0, 0),
        ),
        Transaction(
            description="Netflix September",
            amount=-15.00,
            transaction_type="expense",
            category="Entertainment",
            auto_tagged=True,
            timestamp=datetime(2026, 9, 5, 8, 0, 0),
        ),
    ])
    db_session.commit()

    # Get summary across all months
    res = client.get("/transactions/summary")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4

    # Check August Food aggregation: 20 + 30 = 50 expense, 0 income
    aug_food = next((item for item in data if item["month"] == "2026-08" and item["category"] == "Food"), None)
    assert aug_food is not None
    assert aug_food["total_income"] == 0.0
    assert aug_food["total_expense"] == 50.0  # Must be positive!

    # Check August Salary aggregation: 5000 + 500 = 5500 income, 0 expense
    aug_salary = next((item for item in data if item["month"] == "2026-08" and item["category"] == "Salary"), None)
    assert aug_salary is not None
    assert aug_salary["total_income"] == 5500.0
    assert aug_salary["total_expense"] == 0.0


def test_summary_month_filter(client, db_session):
    db_session.add_all([
        Transaction(
            description="Salary August",
            amount=5000.00,
            transaction_type="income",
            category="Salary",
            auto_tagged=True,
            timestamp=datetime(2026, 8, 1, 9, 0, 0),
        ),
        Transaction(
            description="Salary September",
            amount=5000.00,
            transaction_type="income",
            category="Salary",
            auto_tagged=True,
            timestamp=datetime(2026, 9, 1, 9, 0, 0),
        ),
    ])
    db_session.commit()

    # Query August only
    res = client.get("/transactions/summary?month=2026-08")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["month"] == "2026-08"
    assert data[0]["category"] == "Salary"
    assert data[0]["total_income"] == 5000.0

    # Query with non-existent month
    res_empty = client.get("/transactions/summary?month=2025-01")
    assert res_empty.status_code == 200
    assert res_empty.json() == []

    # Invalid month format
    bad_res = client.get("/transactions/summary?month=bad-month")
    assert bad_res.status_code == 422
