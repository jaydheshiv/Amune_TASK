"""Auto-categorization and semantic validation service."""

import re

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Food": [
        "mcdonald",
        "burger king",
        "starbucks",
        "kfc",
        "subway",
        "domino",
        "pizza",
        "restaurant",
        "cafe",
        "coffee",
        "grocer",
        "grocery",
        "supermarket",
        "walmart",
        "target",
        "trader joe",
        "whole foods",
        "swiggy",
        "zomato",
        "doordash",
        "ubereats",
        "instacart",
        "bakery",
        "dinner",
        "lunch",
        "breakfast",
    ],
    "Transport": [
        "uber",
        "ola",
        "lyft",
        "taxi",
        "cab",
        "metro",
        "subway",
        "train",
        "amtrak",
        "transit",
        "bus",
        "fuel",
        "petrol",
        "gas station",
        "shell",
        "chevron",
        "parking",
        "toll",
    ],
    "Rent": [
        "rent",
        "landlord",
        "lease",
        "apartment",
        "housing",
        "tenant",
    ],
    "Utilities": [
        "electricity",
        "electric",
        "power",
        "water bill",
        "water utility",
        "gas bill",
        "internet",
        "wifi",
        "broadband",
        "phone bill",
        "verizon",
        "at&t",
        "t-mobile",
        "sewage",
        "trash",
    ],
    "Entertainment": [
        "netflix",
        "spotify",
        "cinema",
        "movie",
        "hulu",
        "disney",
        "hbo",
        "prime video",
        "apple tv",
        "youtube premium",
        "concert",
        "theater",
        "steam",
        "playstation",
        "xbox",
        "nintendo",
        "ticketmaster",
    ],
    "Salary": [
        "salary",
        "paycheck",
        "payroll",
        "stipend",
        "wages",
        "direct deposit",
        "earnings",
        "compensation",
        "bonus",
    ],
    "Travel": [
        "airline",
        "flight",
        "delta",
        "united",
        "american airlines",
        "airbnb",
        "hotel",
        "hostel",
        "booking.com",
        "expedia",
        "resort",
    ],
    "Healthcare": [
        "pharmacy",
        "hospital",
        "clinic",
        "doctor",
        "dental",
        "dentist",
        "cvs",
        "walgreens",
        "medical",
        "prescription",
    ],
}

FALLBACK_CATEGORY: str = "Uncategorized"

EXPENSE_ONLY_KEYWORDS: list[str] = [
    "rent",
    "mortgage",
    "groceries",
    "grocery",
    "uber",
    "ola",
    "taxi",
    "netflix",
    "spotify",
    "electricity",
    "fuel",
    "petrol",
    "restaurant",
    "coffee",
    "pharmacy",
]

INCOME_ONLY_KEYWORDS: list[str] = [
    "salary",
    "paycheck",
    "payroll",
    "dividend",
    "bonus",
    "stipend",
    "wages",
]


def normalize_text(text: str) -> str:
    """Normalize text by stripping, lowercasing, and removing apostrophes/special punctuation."""
    lowered = text.strip().lower()
    # Remove apostrophes (e.g. McDonald's -> mcdonalds)
    cleaned = re.sub(r"['’]", "", lowered)
    return cleaned


def categorize(description: str) -> str:
    """Auto-categorize transaction description based on keywords.

    Returns the matched category or FALLBACK_CATEGORY if none match.
    """
    normalized = normalize_text(description)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            normalized_kw = normalize_text(kw)
            if normalized_kw in normalized:
                return category
    return FALLBACK_CATEGORY


def check_semantic_type_conflict(description: str, transaction_type: str) -> str | None:
    """Check if the description conflicts with the transaction type.

    Returns an error message if there is a conflict, or None if valid.
    """
    normalized = normalize_text(description)
    if transaction_type == "income":
        for kw in EXPENSE_ONLY_KEYWORDS:
            if normalize_text(kw) in normalized:
                return f"Description contains expense-only keyword '{kw}' but transaction type is 'income'."
    elif transaction_type == "expense":
        for kw in INCOME_ONLY_KEYWORDS:
            if normalize_text(kw) in normalized:
                return f"Description contains income-only keyword '{kw}' but transaction type is 'expense'."
    return None
