# Personal Finance Tracker System

A robust, full-stack Personal Finance Tracker that records income and expenses, auto-categorizes transactions using smart heuristics, detects duplicate entries within a sliding window, and provides monthly financial health summaries.

Built with **FastAPI**, **SQLAlchemy**, **SQLite**, **Alembic**, **ReactJS**, and an auto-generated **Python SDK** via the **OpenAPI Generator CLI**.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start (Windows Scripts)](#quick-start-windows-scripts)
4. [Manual Setup (Cross-Platform)](#manual-setup-cross-platform)
5. [Backend Trick Logic & Core Rules](#backend-trick-logic--core-rules)
6. [API Contract & Documentation](#api-contract--documentation)
7. [Running Tests](#running-tests)
8. [Python SDK Generation & Smoke Testing](#python-sdk-generation--smoke-testing)
9. [Design Decisions & Assumptions](#design-decisions--assumptions)
10. [Deliverables Checklist](#deliverables-checklist)

---

## 1. Architecture Overview

This project adheres strictly to **Clean Architecture** and separation of concerns:

```
finance-tracker/
├── backend/
│   ├── main.py               # FastAPI app, CORS middleware, global exception handlers
│   ├── config.py             # App configurations (DB URL, duplicate window)
│   ├── database.py           # Engine, SessionLocal, get_db dependency injection
│   ├── models.py             # SQLAlchemy Transaction model with CHECK constraint
│   ├── schemas.py            # Pydantic v2 validation and response models
│   ├── exceptions.py         # Custom domain exceptions and JSON error handlers
│   ├── routers/
│   │   └── transactions.py   # Thin HTTP endpoints with unique operation_ids
│   └── services/
│       ├── categorizer.py    # Keyword matching and semantic conflict checks
│       └── transaction_service.py # Business logic: signs, duplicates, aggregations
├── frontend/                 # ReactJS frontend client (Vite, Axios, Recharts)
│   ├── src/api.js            # Centralized API service with error extraction
│   └── src/components/       # TransactionForm, TransactionList, MonthlySummary, ExpensePieChart
├── finance_sdk/              # Python SDK generated via OpenAPI Generator CLI
├── tests/                    # Pytest suite with isolated in-memory SQLite fixtures
│   ├── conftest.py
│   ├── test_categorizer.py
│   ├── test_transactions.py
│   └── test_summary.py
├── alembic/                  # Database migration versions
├── alembic.ini               # Alembic configuration
├── seed_data.sql             # SQL seed dataset (20 rows across 3 months)
├── sdk_smoke_test.py         # End-to-end SDK verification script
├── setupdev.bat              # One-click Windows developer environment setup
├── runapplication.bat        # One-click Windows application execution script
└── requirements.txt          # Pinned backend Python dependencies
```

- **HTTP Layer (`backend/routers/`)**: Receives requests, validates inputs via Pydantic, calls the service layer, and returns formatted responses. No business logic or database queries reside in routers.
- **Service Layer (`backend/services/`)**: Handles all business rules (semantic checks, sign storage, duplicate window detection, aggregations). Receives database sessions via dependency injection (`db: Session`).
- **Data Layer (`backend/models.py`)**: Pure SQLAlchemy database entity matching the challenge schema table.

---

## 2. Prerequisites

- **Python**: 3.10+ (tested on Python 3.12)
- **Node.js**: 18+ (tested on Node 24 with npm 11)
- **Java**: JRE/JDK 11+ (required only for OpenAPI Generator CLI)
- **Docker**: **Not used** (per challenge instructions)

---

## 3. Quick Start (Windows Scripts)

### Step 1: Environment Setup
Run the automated setup script to create the virtual environment, install backend packages, run Alembic migrations, and install frontend dependencies:
```cmd
setupdev.bat
```

### Step 2: Launch Application
Run the execution script to launch the FastAPI backend (on port `8000`) and the React frontend (on port `3000`):
```cmd
runapplication.bat
```

- **Frontend Client**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON Specification**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 4. Manual Setup (Cross-Platform)

If running on macOS, Linux, or setting up manually on Windows:

### Backend Setup
```bash
# 1. Create and activate virtual environment
python -m venv env
# On Windows:
call env\Scripts\activate
# On Linux/macOS:
# source env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
alembic upgrade head

# 4. (Optional) Populate seed data
python -c "import sqlite3; conn = sqlite3.connect('finance.db'); conn.executescript(open('seed_data.sql').read()); conn.commit(); print('Database seeded successfully.')"

# 5. Start backend server
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

---

## 5. Backend Trick Logic & Core Rules

1. **Sign Handling Convention**:
   - Clients always submit a **positive amount** (`amount > 0`).
   - The backend stores expenses as **negative values** (`-abs(amount)`) and income as **positive values** (`+abs(amount)`).
   - All API endpoints (list, single transaction, summary totals) **always return absolute positive values** to the client.
2. **Duplicate Detection**:
   - Matches transactions with the **same normalized description** (trimmed, case-insensitive) + **same stored amount** + **same transaction type** within a configurable sliding window (`DUPLICATE_WINDOW_SECONDS`, default `300` seconds / 5 minutes).
   - Rejects duplicates with `409 Conflict`.
   - Identical transactions outside the window are allowed.
3. **Smart Auto-Categorization & Normalization**:
   - Categorizes based on substring matches (e.g. `mcdonald` $\rightarrow$ Food, `uber` $\rightarrow$ Transport, `netflix` $\rightarrow$ Entertainment).
   - Punctuation-insensitive: Handles apostrophes like `McDonald's` $\rightarrow$ Food.
   - Falls back to `Uncategorized` if no keyword matches.
4. **Semantic Type Conflict Validation**:
   - Rejects transactions where an expense-only keyword is entered as income (e.g., `Apartment Rent` as `income` $\rightarrow$ `422 Unprocessable Entity`).
   - Rejects transactions where an income-only keyword is entered as expense (e.g., `Monthly Salary` as `expense` $\rightarrow$ `422 Unprocessable Entity`).
5. **Manual Reclassification Override**:
   - When a transaction category is updated via `PATCH /transactions/{id}/reclassify`, `auto_tagged` is permanently set to `0` (`False`).
6. **Monthly Aggregation**:
   - The `/transactions/summary` endpoint groups transactions by `YYYY-MM` and category.
   - Returns separate `total_income` and `total_expense` positive sums per category.

---

## 6. API Contract & Documentation

| Method | Endpoint | operation_id | Success Code | Error Codes | Description |
|---|---|---|---|---|---|
| `POST` | `/transactions/` | `create_transaction` | `201 Created` | `409`, `422` | Create income or expense with auto-tagging |
| `GET` | `/transactions/` | `list_transactions` | `200 OK` | `422` | List transactions with filters (`month`, `type`, `category`) |
| `GET` | `/transactions/summary` | `get_summary` | `200 OK` | `422` | Monthly income and expense breakdown per category |
| `DELETE` | `/transactions/{transaction_id}` | `delete_transaction` | `204 No Content`| `404` | Delete a transaction by ID |
| `PATCH` | `/transactions/{transaction_id}/reclassify` | `reclassify_transaction` | `200 OK` | `404`, `422` | Manually reclassify category (`auto_tagged=false`) |

> **Route Ordering Note**: `/transactions/summary` is declared before `/transactions/{transaction_id}` to prevent FastAPI route collision.

### Sample Request & Response

#### Create Transaction (`POST /transactions/`)
Request:
```json
{
  "description": "McDonald's Lunch",
  "amount": 15.50,
  "transaction_type": "expense"
}
```
Response (`201 Created`):
```json
{
  "id": 1,
  "description": "McDonald's Lunch",
  "amount": 15.50,
  "transaction_type": "expense",
  "category": "Food",
  "auto_tagged": true,
  "timestamp": "2026-10-10T12:00:00"
}
```

#### Duplicate Attempt (`POST /transactions/` within 5 minutes)
Response (`409 Conflict`):
```json
{
  "detail": "Duplicate transaction detected within 300 seconds."
}
```

#### Semantic Conflict (`POST /transactions/` with Rent as income)
Response (`422 Unprocessable Entity`):
```json
{
  "detail": "Description contains expense-only keyword 'rent' but transaction type is 'income'."
}
```

---

## 7. Running Tests

The test suite covers all business logic, boundary cases, and database constraints using an isolated in-memory SQLite database (`StaticPool`):

```bash
# Run the test suite
pytest -v
```

### Test Coverage Highlights
- `test_categorize_food`, `test_categorize_transport`, etc. (Keyword matching, apostrophe normalization)
- `test_semantic_conflict_rejection` (Rent as income, Salary as expense)
- `test_expense_stored_negative_in_db` (DB negative storage, absolute API output)
- `test_duplicate_transaction_within_window` (409 conflict detection)
- `test_transaction_outside_duplicate_window_allowed` (Successful creation outside 300s window)
- `test_reclassify_transaction` (Category update sets `auto_tagged=False`)
- `test_summary_grouping_and_absolute_totals` (Monthly grouping and positive sums)

---

## 8. Python SDK Generation & Smoke Testing

The Python SDK in `finance_sdk/` is generated using **OpenAPI Generator CLI** directly from the live specification:

### Regenerating the SDK
```bash
# 1. Install generator CLI
npm install -g @openapitools/openapi-generator-cli

# 2. Generate SDK into finance_sdk/
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o finance_sdk --package-name finance_sdk

# 3. Install in editable mode
pip install -e finance_sdk
```

### Running the SDK Smoke Test
A standalone smoke test script is provided in the repository root:
```bash
python sdk_smoke_test.py
```

### Example SDK Usage
```python
from finance_sdk import ApiClient, Configuration
from finance_sdk.api.transactions_api import TransactionsApi
from finance_sdk.models.transaction_create import TransactionCreate

config = Configuration(host="http://localhost:8000")
with ApiClient(config) as client:
    api = TransactionsApi(client)
    
    # 1. List transactions
    transactions = api.list_transactions()
    
    # 2. Add transaction
    new_tx = api.create_transaction(
        TransactionCreate(
            description="Starbucks Latte",
            amount=6.25,
            transaction_type="expense",
        )
    )
    print(f"Created: {new_tx.id}, Category: {new_tx.category}")
```

---

## 9. Design Decisions & Assumptions

| Topic | Decision | Rationale |
|---|---|---|
| **Database Engine** | SQLite (`finance.db`) | Meets challenge requirement without external daemon dependencies. |
| **Duplicate Window** | 300 seconds (5 min) | Configurable via `DUPLICATE_WINDOW_SECONDS`; prevents accidental double clicks. |
| **Duplicate Match Criteria** | Trimmed lowercase description + exact stored amount + type | Prevents duplicate charges while allowing different amounts for the same vendor. |
| **Expense Sign Convention** | Stored negative, exposed absolute | Adheres to accounting best practices in DB while keeping UI clean and positive. |
| **Fallback Category** | `Uncategorized` | Predictable fallback when description keywords don't match known categories. |
| **Semantic Conflict Error Code** | `422 Unprocessable Entity` | Clean REST convention for syntactically valid data that violates semantic domain rules. |
| **Default Summary Output** | Returns all months if `?month=` omitted | Enables overview dashboard charts without requiring a hardcoded default month. |
| **Frontend Real-Time Updates** | 10-second polling with visibility detection | Fulfills bonus requirement reliably without complex WebSocket infrastructure. |

---

## 10. Deliverables Checklist

- [x] **Backend (FastAPI) source code**: Cleanly layered routers, services, schemas, and models.
- [x] **SQLite database & migration files**: Complete Alembic migration history and `finance.db`.
- [x] **ReactJS frontend code**: Responsive UI with Axios, filterable list, summary tables, and Recharts pie chart.
- [x] **Python SDK**: Generated via OpenAPI Generator CLI in `finance_sdk/`.
- [x] **Setup & Execution Scripts**: `setupdev.bat` and `runapplication.bat`.
- [x] **Unit tests for backend**: Full test suite passing with 100% green status.
- [x] **README**: Comprehensive setup, execution, architecture, and API documentation.
- [x] **Zero Docker usage**: Verified native execution across all components.
