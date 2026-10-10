"""Unit tests for transaction endpoints and business rules."""

from datetime import datetime, timedelta
from backend.models import Transaction


def test_create_transaction_success(client):
    res = client.post(
        "/transactions/",
        json={"description": "McDonald's Lunch", "amount": 15.50, "transaction_type": "expense"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["description"] == "McDonald's Lunch"
    assert data["amount"] == 15.50
    assert data["transaction_type"] == "expense"
    assert data["category"] == "Food"
    assert data["auto_tagged"] is True


def test_expense_stored_negative_in_db(client, db_session):
    res = client.post(
        "/transactions/",
        json={"description": "Electricity Bill", "amount": 75.00, "transaction_type": "expense"},
    )
    assert res.status_code == 201
    tx_id = res.json()["id"]

    # Verify API returned positive amount
    assert res.json()["amount"] == 75.00

    # Verify DB stored negative amount
    db_tx = db_session.query(Transaction).filter(Transaction.id == tx_id).first()
    assert db_tx is not None
    assert db_tx.amount == -75.00


def test_income_stored_positive_in_db(client, db_session):
    res = client.post(
        "/transactions/",
        json={"description": "Monthly Salary", "amount": 4000.00, "transaction_type": "income"},
    )
    assert res.status_code == 201
    tx_id = res.json()["id"]

    # Verify DB stored positive amount
    db_tx = db_session.query(Transaction).filter(Transaction.id == tx_id).first()
    assert db_tx is not None
    assert db_tx.amount == 4000.00


def test_validation_errors(client):
    # Invalid transaction type
    res = client.post(
        "/transactions/",
        json={"description": "Grocery", "amount": 50.0, "transaction_type": "transfer"},
    )
    assert res.status_code == 422

    # Amount <= 0
    res = client.post(
        "/transactions/",
        json={"description": "Grocery", "amount": -10.0, "transaction_type": "expense"},
    )
    assert res.status_code == 422

    res = client.post(
        "/transactions/",
        json={"description": "Grocery", "amount": 0, "transaction_type": "expense"},
    )
    assert res.status_code == 422

    # Empty description
    res = client.post(
        "/transactions/",
        json={"description": "   ", "amount": 25.0, "transaction_type": "expense"},
    )
    assert res.status_code == 422


def test_semantic_conflict_rejection(client):
    # Rent entered as income -> 422
    res = client.post(
        "/transactions/",
        json={"description": "Apartment Rent Payment", "amount": 1200.0, "transaction_type": "income"},
    )
    assert res.status_code == 422
    assert "expense-only keyword" in res.json()["detail"]

    # Salary entered as expense -> 422
    res = client.post(
        "/transactions/",
        json={"description": "Monthly Salary Paycheck", "amount": 3500.0, "transaction_type": "expense"},
    )
    assert res.status_code == 422
    assert "income-only keyword" in res.json()["detail"]


def test_duplicate_transaction_within_window(client):
    payload = {"description": "Starbucks Coffee", "amount": 6.50, "transaction_type": "expense"}
    res1 = client.post("/transactions/", json=payload)
    assert res1.status_code == 201

    # Second identical request within 5-minute window must return 409
    res2 = client.post("/transactions/", json=payload)
    assert res2.status_code == 409
    assert "Duplicate transaction detected" in res2.json()["detail"]


def test_duplicate_detection_case_and_whitespace_insensitivity(client):
    res1 = client.post(
        "/transactions/",
        json={"description": "Starbucks Coffee", "amount": 6.50, "transaction_type": "expense"},
    )
    assert res1.status_code == 201

    # Same amount and normalized description with extra spaces/different casing
    res2 = client.post(
        "/transactions/",
        json={"description": "  starbucks coffee  ", "amount": 6.50, "transaction_type": "expense"},
    )
    assert res2.status_code == 409


def test_same_description_different_amount_allowed(client):
    res1 = client.post(
        "/transactions/",
        json={"description": "Groceries", "amount": 45.00, "transaction_type": "expense"},
    )
    assert res1.status_code == 201

    res2 = client.post(
        "/transactions/",
        json={"description": "Groceries", "amount": 72.00, "transaction_type": "expense"},
    )
    assert res2.status_code == 201


def test_transaction_outside_duplicate_window_allowed(client, db_session):
    # Insert older transaction directly in DB with timestamp outside 300 seconds
    from datetime import timezone
    old_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=350)
    old_tx = Transaction(
        description="Metro Ticket",
        amount=-5.00,
        transaction_type="expense",
        category="Transport",
        auto_tagged=True,
        timestamp=old_time,
    )
    db_session.add(old_tx)
    db_session.commit()

    # Now post same transaction via API: should succeed (201)
    res = client.post(
        "/transactions/",
        json={"description": "Metro Ticket", "amount": 5.00, "transaction_type": "expense"},
    )
    assert res.status_code == 201


def test_reclassify_transaction(client):
    res = client.post(
        "/transactions/",
        json={"description": "Uber Airport Ride", "amount": 40.00, "transaction_type": "expense"},
    )
    assert res.status_code == 201
    tx_id = res.json()["id"]
    assert res.json()["category"] == "Transport"
    assert res.json()["auto_tagged"] is True

    # Reclassify to Travel
    patch_res = client.patch(
        f"/transactions/{tx_id}/reclassify",
        json={"category": "Travel"},
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["category"] == "Travel"
    assert updated["auto_tagged"] is False


def test_reclassify_nonexistent_returns_404(client):
    res = client.patch("/transactions/99999/reclassify", json={"category": "Travel"})
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_delete_transaction(client):
    res = client.post(
        "/transactions/",
        json={"description": "Book Purchase", "amount": 20.00, "transaction_type": "expense"},
    )
    assert res.status_code == 201
    tx_id = res.json()["id"]

    # Delete existing
    del_res = client.delete(f"/transactions/{tx_id}")
    assert del_res.status_code == 204

    # Delete again -> 404
    del_res2 = client.delete(f"/transactions/{tx_id}")
    assert del_res2.status_code == 404


def test_list_transactions_and_filters(client, db_session):
    # Insert multiple transactions across dates and types
    db_session.add_all([
        Transaction(
            description="August Salary",
            amount=5000.00,
            transaction_type="income",
            category="Salary",
            auto_tagged=True,
            timestamp=datetime(2026, 8, 1, 10, 0, 0),
        ),
        Transaction(
            description="August Rent",
            amount=-1200.00,
            transaction_type="expense",
            category="Rent",
            auto_tagged=True,
            timestamp=datetime(2026, 8, 2, 10, 0, 0),
        ),
        Transaction(
            description="September Coffee",
            amount=-6.00,
            transaction_type="expense",
            category="Food",
            auto_tagged=True,
            timestamp=datetime(2026, 9, 5, 10, 0, 0),
        ),
    ])
    db_session.commit()

    # List all
    all_res = client.get("/transactions/")
    assert all_res.status_code == 200
    assert len(all_res.json()) == 3

    # Filter by month
    aug_res = client.get("/transactions/?month=2026-08")
    assert aug_res.status_code == 200
    assert len(aug_res.json()) == 2

    # Filter by type
    exp_res = client.get("/transactions/?type=expense")
    assert exp_res.status_code == 200
    assert len(exp_res.json()) == 2

    # Filter by category
    food_res = client.get("/transactions/?category=food")
    assert food_res.status_code == 200
    assert len(food_res.json()) == 1
    assert food_res.json()[0]["description"] == "September Coffee"

    # Combined filter
    comb_res = client.get("/transactions/?month=2026-08&type=expense&category=Rent")
    assert comb_res.status_code == 200
    assert len(comb_res.json()) == 1
    assert comb_res.json()[0]["amount"] == 1200.00  # returned absolute!

    # Bad month format
    bad_month = client.get("/transactions/?month=2026-8")
    assert bad_month.status_code == 422
