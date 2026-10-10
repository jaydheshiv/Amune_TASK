"""Tests for categorizer and semantic conflict detection."""

from backend.services.categorizer import (
    categorize,
    check_semantic_type_conflict,
    FALLBACK_CATEGORY,
)


def test_categorize_food():
    assert categorize("McDonald's burger") == "Food"
    assert categorize("mcdonalds drive-thru") == "Food"
    assert categorize("STARBUCKS COFFEE") == "Food"
    assert categorize("Italian Pizza lunch") == "Food"
    assert categorize("Swiggy food order") == "Food"
    assert categorize("Burger King meal") == "Food"
    assert categorize("Trader Joe's groceries") == "Food"
    assert categorize("Doordash delivery") == "Food"


def test_categorize_transport():
    assert categorize("Uber ride") == "Transport"
    assert categorize("Ola cab booking") == "Transport"
    assert categorize("City Metro ticket") == "Transport"
    assert categorize("Petrol pump refill") == "Transport"
    assert categorize("Shell Gas Station") == "Transport"
    assert categorize("Amtrak train ticket") == "Transport"


def test_categorize_utilities():
    assert categorize("Electricity Bill October") == "Utilities"
    assert categorize("Home Internet Wifi") == "Utilities"
    assert categorize("Water bill payment") == "Utilities"
    assert categorize("Verizon phone bill") == "Utilities"


def test_categorize_entertainment():
    assert categorize("Netflix Subscription") == "Entertainment"
    assert categorize("Spotify premium") == "Entertainment"
    assert categorize("Cinema Movie tickets") == "Entertainment"
    assert categorize("Disney+ annual sub") == "Entertainment"
    assert categorize("Steam summer sale") == "Entertainment"


def test_categorize_travel():
    assert categorize("Delta Airlines flight") == "Travel"
    assert categorize("Airbnb vacation stay") == "Travel"
    assert categorize("Booking.com hotel") == "Travel"


def test_categorize_healthcare():
    assert categorize("CVS Pharmacy prescription") == "Healthcare"
    assert categorize("Dental clinic checkup") == "Healthcare"


def test_categorize_salary():
    assert categorize("Monthly Salary deposit") == "Salary"
    assert categorize("Biweekly paycheck") == "Salary"


def test_categorize_unknown_fallback():
    assert categorize("Random electronics store purchase") == FALLBACK_CATEGORY
    assert categorize("Guitar lesson payment") == FALLBACK_CATEGORY


def test_semantic_type_conflict():
    # Expense keywords as income should conflict
    assert check_semantic_type_conflict("Monthly Rent payment", "income") is not None
    assert check_semantic_type_conflict("Uber ride", "income") is not None
    assert check_semantic_type_conflict("Netflix subscription", "income") is not None

    # Income keywords as expense should conflict
    assert check_semantic_type_conflict("Company Salary", "expense") is not None
    assert check_semantic_type_conflict("Quarterly bonus", "expense") is not None

    # Valid combinations should not conflict
    assert check_semantic_type_conflict("Monthly Rent", "expense") is None
    assert check_semantic_type_conflict("Company Salary", "income") is None
    assert check_semantic_type_conflict("Unknown purchase", "expense") is None
