import logging
import re

from backend.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

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


def extract_category_from_response(raw_text: str) -> str | None:
    """Extract and validate category name from Groq model response."""
    cleaned = raw_text.strip().strip("'\"`.")

    # 1. Exact case-insensitive match against standard categories
    for cat in CATEGORY_KEYWORDS:
        if cat.lower() == cleaned.lower():
            return cat

    # 2. Check if explicit "uncategorized"
    if "uncategorized" in cleaned.lower():
        return FALLBACK_CATEGORY

    # 3. Check regex word boundary for standard categories in case of short sentence like "Category: Food"
    for cat in CATEGORY_KEYWORDS:
        if re.search(rf"\b{re.escape(cat)}\b", cleaned, re.IGNORECASE):
            return cat

    return None


def categorize_with_groq(description: str) -> str | None:
    """Categorize transaction description using the Groq API.

    Returns the identified category, or None if the API key is not configured,
    the call fails, or an unparseable response is received.
    """
    if not GROQ_API_KEY:
        return None

    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY, timeout=GROQ_TIMEOUT_SECONDS)
        prompt = (
            "You are a personal finance categorization assistant. Categorize the transaction into ONE of:\n"
            "- Food: restaurants, cafes, fast food, groceries, food delivery\n"
            "- Transport: cabs, rideshare (Uber, Lyft), subway, metro, trains (Amtrak), fuel, petrol, parking, toll\n"
            "- Rent: rent, lease, housing, landlord\n"
            "- Utilities: electricity, water, gas, internet, wifi, phone bill\n"
            "- Entertainment: streaming, movies, concerts, theater, gaming\n"
            "- Salary: paycheck, wages, stipend, payroll, direct deposit, earnings\n"
            "- Travel: airlines, flights, hotels, booking.com, airbnb, vacation resorts\n"
            "- Healthcare: pharmacy, doctor, dental, clinic, medical, prescription\n"
            "- Uncategorized: electronics, general shopping, or anything not matching above.\n\n"
            "Respond with ONLY the exact category name and nothing else."
        )

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Transaction: {description}"},
            ],
            temperature=0.0,
            max_tokens=100,
        )

        content = response.choices[0].message.content or ""
        matched_category = extract_category_from_response(content)
        if matched_category:
            return matched_category
    except Exception as exc:
        logger.warning("Groq API categorization failed for '%s': %s", description, exc)

    return None


def categorize_with_keywords(description: str) -> str:
    """Auto-categorize transaction description based on hard-coded keywords.

    Returns the matched category or FALLBACK_CATEGORY if none match.
    """
    normalized = normalize_text(description)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            normalized_kw = normalize_text(kw)
            if normalized_kw in normalized:
                return category
    return FALLBACK_CATEGORY


def categorize(description: str) -> str:
    """Auto-categorize transaction description using Groq API with hard-coded keyword fallback.

    First attempts Groq API categorization if configured. If unavailable, errored,
    or undetermined, falls back to the hard-coded keyword matcher.
    """
    # 1. Attempt Groq API categorization
    groq_cat = categorize_with_groq(description)
    if groq_cat and groq_cat != FALLBACK_CATEGORY:
        return groq_cat

    # 2. Hard-coded keywords fallback
    keyword_cat = categorize_with_keywords(description)
    if keyword_cat != FALLBACK_CATEGORY:
        return keyword_cat

    # 3. Default fallback
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
