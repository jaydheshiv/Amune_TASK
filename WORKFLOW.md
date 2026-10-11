# Personal Finance Tracker System — Complete Workflow & Architecture Guide

This document provides an exhaustive, end-to-end breakdown of the **Amune Personal Finance Tracker System**. It covers the complete request lifecycle, architectural patterns, database schemas, "trick logic" rules, AI categorization pipeline, frontend state flow, and SDK integration.

---

## 1. High-Level System Architecture

The application is structured into four distinct, loosely coupled layers following **Clean Architecture** principles:

```mermaid
graph TD
    User([User / Browser]) <--> ReactApp[React Frontend Client<br/>Vite + Axios + Recharts]
    ReactApp <-->|REST HTTP / JSON| FastAPI[FastAPI Backend Gateway<br/>CORS + Exception Handlers]
    
    subgraph Backend Core
        FastAPI --> Routers[Routers Layer<br/>backend/routers/transactions.py]
        Routers --> Services[Service Layer<br/>backend/services/transaction_service.py]
        Services --> Categorizer[Categorization Engine<br/>backend/services/categorizer.py]
        Categorizer -.->|1. Primary AI Inference| GroqAPI[(Groq Cloud API<br/>openai/gpt-oss-20b)]
        Categorizer -.->|2. Fallback Matching| KeywordDict[(Hard-Coded Keyword Map)]
        Services --> DBModels[Data Layer / SQLAlchemy ORM<br/>backend/models.py]
    end

    DBModels <-->|Read / Write| SQLite[(SQLite Database<br/>finance.db)]
    Alembic[Alembic Migrations] -.->|Schema Versioning| SQLite
    FastAPI -.->|OpenAPI Spec /openapi.json| OpenAPIGen[OpenAPI Generator CLI]
    OpenAPIGen --> PythonSDK[Python Platform SDK<br/>finance_sdk/]
```

---

## 2. Complete Transaction Creation Workflow (`POST /transactions/`)

When a user submits a transaction (or via the SDK / API), the backend executes a rigorous 6-step pipeline before committing to the database:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Frontend / Client
    participant Router as routers/transactions.py
    participant Service as services/transaction_service.py
    participant Categorizer as services/categorizer.py
    participant Groq as Groq Cloud API
    participant DB as SQLite (finance.db)

    Client->>Router: POST /transactions/ {description, amount, transaction_type}
    Router->>Service: create_transaction(db, data)
    
    Note over Service: Step 1: Semantic Validation
    Service->>Categorizer: check_semantic_type_conflict(desc, type)
    alt Conflict detected (e.g., 'Rent' as income)
        Categorizer-->>Service: Error message
        Service-->>Router: Raise InvalidTransactionError
        Router-->>Client: 422 Unprocessable Content JSON
    end
    
    Note over Service: Step 2: Sign Convention
    Service->>Service: Stored amount = -abs(amount) if expense else +abs(amount)
    
    Note over Service: Step 3: Duplicate Window Check
    Service->>DB: Query transactions in last DUPLICATE_WINDOW_SECONDS (300s)
    DB-->>Service: Candidate transactions
    alt Same normalized desc + same amount + same type
        Service-->>Router: Raise DuplicateTransactionError
        Router-->>Client: 409 Conflict JSON
    end

    Note over Service: Step 4: Auto-Categorization
    Service->>Categorizer: categorize(description)
    alt Groq API Key Configured
        Categorizer->>Groq: Chat Completion (openai/gpt-oss-20b)
        alt Groq responds with category
            Groq-->>Categorizer: Matched Category (e.g. 'Food')
        else Groq fails / timeout / unmapped
            Categorizer->>Categorizer: Fall back to CATEGORY_KEYWORDS
        end
    else No API Key
        Categorizer->>Categorizer: Direct CATEGORY_KEYWORDS matching
    end
    Categorizer-->>Service: Final Category (or 'Uncategorized')

    Note over Service: Step 5: Persistence
    Service->>DB: INSERT into transactions (amount negative/positive, auto_tagged=1)
    DB-->>Service: Generated ID & Timestamp
    Service-->>Router: Transaction Model
    Router-->>Client: 201 Created (Amount returned as absolute positive)
```

---

## 3. Database Architecture & Alembic Migrations

### 3.1 Table Schema (`transactions`)
The database is backed by SQLite (`finance.db`) conforming strictly to the specification schema:

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for each transaction |
| `description` | `TEXT` | `NOT NULL` | User-provided text describing the transaction |
| `amount` | `REAL` | `NOT NULL` | Stored amount: **Negative** for expenses, **Positive** for income |
| `transaction_type` | `TEXT` | `NOT NULL`, `CHECK(type IN ('income','expense'))` | Type discriminator enforced at the database level |
| `category` | `TEXT` | `NULLABLE` | Classified category name (e.g., Food, Transport) |
| `auto_tagged` | `BOOLEAN`| `NOT NULL DEFAULT 1` | `1` if categorized automatically; `0` if reclassified manually |
| `timestamp` | `TIMESTAMP`| `DEFAULT CURRENT_TIMESTAMP` | UTC timestamp of transaction creation |

### 3.2 Migration Workflow (Alembic)
- Configuration: [`alembic.ini`](file:///d:/sem-9/Amune_TASK/alembic.ini) pointing to [`alembic/`](file:///d:/sem-9/Amune_TASK/alembic/).
- Migration Script: [`alembic/versions/0a913ffcb657_create_transactions_table.py`](file:///d:/sem-9/Amune_TASK/alembic/versions/0a913ffcb657_create_transactions_table.py).
- Applied via: `alembic upgrade head` (automatically invoked by `setupdev.bat`).

---

## 4. Backend "Trick Logic" & Business Rules

### 4.1 Sign Convention
- **Inbound Client Rule**: Clients must always submit a strictly positive value (`amount > 0`). Pydantic validates `Field(..., gt=0)`.
- **Database Storage Rule**:
  - `expense` $\rightarrow$ stored as `-abs(amount)`
  - `income` $\rightarrow$ stored as `+abs(amount)`
- **Outbound Client Rule**: The API always exposes absolute positive values (`abs(amount)`) in `TransactionOut` and summary aggregations so UI components and SDK clients receive consistent numerical representations.

### 4.2 Duplicate Detection (Sliding Window)
- **Window Length**: Configured via `DUPLICATE_WINDOW_SECONDS` (default: `300` seconds / 5 minutes).
- **Match Criteria**:
  1. Transaction falls within `[now - 300s, now]`.
  2. Transaction type matches (`income` == `income` or `expense` == `expense`).
  3. Stored amount matches: `abs(candidate.amount - new.amount) < 1e-4`.
  4. Normalized description matches: `normalize_text(candidate.description) == normalize_text(new.description)`.
- **Outcome**: Triggers `DuplicateTransactionError`, mapped to **`409 Conflict`**. Duplicate entries submitted outside the 300s window are permitted.

### 4.3 Semantic Type Conflict Validation
Rejects logically conflicting transactions before writing to the database:
- **Expense-Only Keywords**: `rent`, `mortgage`, `groceries`, `grocery`, `uber`, `ola`, `taxi`, `netflix`, `spotify`, `electricity`, `fuel`, `petrol`, `restaurant`, `coffee`, `pharmacy`.
  - Example: Entering `"Monthly Apartment Rent"` as `"income"` $\rightarrow$ **`422 Unprocessable Content`**.
- **Income-Only Keywords**: `salary`, `paycheck`, `payroll`, `dividend`, `bonus`, `stipend`, `wages`.
  - Example: Entering `"Company Salary"` as `"expense"` $\rightarrow$ **`422 Unprocessable Content`**.

### 4.4 Category Reclassification (`PATCH`)
- Endpoint: `PATCH /transactions/{transaction_id}/reclassify`.
- When a category is manually changed:
  1. `category` updates to the new string value.
  2. `auto_tagged` is permanently set to `0` (`False`).
  3. Ensures that human corrections are audited and never overwritten by automatic heuristics.

---

## 5. AI Auto-Categorization Pipeline (Groq + Keyword Fallback)

```mermaid
flowchart TD
    Start([New Transaction Description]) --> CheckKey{Is GROQ_API_KEY<br/>configured in .env?}
    
    CheckKey -- Yes --> CallGroq[Call Groq Cloud API<br/>Model: openai/gpt-oss-20b<br/>Timeout: 3.0s]
    CheckKey -- No --> KeywordMatch[Hard-Coded Keyword Matching<br/>CATEGORY_KEYWORDS]
    
    CallGroq --> GroqSuccess{API Responded<br/>Successfully?}
    GroqSuccess -- Yes --> ParseCat{Recognized<br/>Standard Category?}
    GroqSuccess -- No (Timeout/Error) --> FallbackLog[Log Warning & Fallback] --> KeywordMatch
    
    ParseCat -- Yes --> ReturnAI[Return AI Category<br/>e.g. Food, Travel, Rent]
    ParseCat -- No / Uncategorized --> KeywordMatch
    
    KeywordMatch --> FoundKW{Keyword<br/>Matched?}
    FoundKW -- Yes --> ReturnKW[Return Dictionary Category]
    FoundKW -- No --> ReturnUncat[Return 'Uncategorized']
```

- **Groq AI Integration**: Uses `openai/gpt-oss-20b` (low-latency reasoning model) with temperature `0.0`.
- **Security Policy**: `.env` is listed in `.gitignore` and never committed to source control. Evaluators configure their own key in `.env` or run on the built-in keyword dictionary.

---

## 6. Frontend Client Workflow & Component Hierarchy

The frontend is built with React 18, Vite, Axios, and Recharts.

```mermaid
graph TD
    App[App.jsx<br/>Root State: activeTab, transactions, summaryData]
    
    App --> Navbar[Navbar & Amune Header<br/>Taskbar Navigation: 5 Tabs]
    
    App --> TabDashboard[Dashboard Tab]
    TabDashboard --> KPIStrip[KPI Metrics Strip<br/>Total Income, Expense, Net Balance in ₹]
    TabDashboard --> DashGrid[Equal 50/50 Grid Layout]
    DashGrid --> PieCard[ExpensePieChart.jsx<br/>Category Distribution]
    DashGrid --> TrendsCard[MonthlyComparisonChart.jsx<br/>Income vs Expense Bar/Line]
    TabDashboard --> RecentTable[Recent Transactions Table]

    App --> TabAdd[Add Tab]
    TabAdd --> TxForm[TransactionForm.jsx<br/>Form Inputs, Validation, Instant Feedback]

    App --> TabSummary[Summary Tab]
    TabSummary --> MonthSummary[MonthlySummary.jsx<br/>Category Income/Expense Aggregations]

    App --> TabRecords[Records Tab]
    TabRecords --> TxList[TransactionList.jsx<br/>Filters: Month/Type/Category, Inline Reclassify, Delete]

    App --> TabTrends[Trends Tab]
    TabTrends --> BigTrends[Full-width Trends & Historical Analytics]
```

### Key Frontend Features:
1. **Taskbar Tabs**: Five isolated tabs (`Dashboard`, `Add`, `Summary`, `Records`, `Trends`) prevent infinite vertical scrolling.
2. **Indian Rupee (`₹`) Localization**: All currency displays (KPIs, tables, forms, chart tooltips) uniformly format currency in `₹`.
3. **Half-and-Half Charts Layout (`1fr 1fr`)**: The pie chart and bar trend cards share equal 50% width on the dashboard.
4. **Real-Time Polling & Mutation Sync**: Adding, reclassifying, or deleting a transaction triggers an immediate data reload across all components.

---

## 7. Python Platform SDK Workflow

The client SDK ([`finance_sdk/`](file:///d:/sem-9/Amune_TASK/finance_sdk/)) is auto-generated using `@openapitools/openapi-generator-cli` from the backend's OpenAPI contract.

### 7.1 SDK Generation Pipeline
```bash
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o finance_sdk
```

### 7.2 SDK Usage Pattern
```python
from finance_sdk import ApiClient
from finance_sdk.api.transactions_api import TransactionsApi
from finance_sdk.models.transaction_create import TransactionCreate

# 1. Initialize API Client
client = ApiClient()
api = TransactionsApi(client)

# 2. Add Transaction
new_tx = api.create_transaction(
    transaction_create=TransactionCreate(
        description="Dinner at Italian Bistro",
        amount=45.0,
        transaction_type="expense"
    )
)

# 3. Retrieve Summary
summaries = api.get_summary(month="2026-10")

# 4. Reclassify
updated = api.reclassify_transaction(
    transaction_id=new_tx.id,
    reclassify_request={"category": "Food"}
)
```

### 7.3 Automated SDK Verification
The test script [`sdk_smoke_test.py`](file:///d:/sem-9/Amune_TASK/sdk_smoke_test.py) tests all 5 endpoints via the SDK against the live server:
```cmd
python sdk_smoke_test.py
```
Outputs: `All SDK smoke test assertions passed successfully!`

---

## 8. Development Scripts & DevOps Workflow

```mermaid
graph LR
    subgraph Setup Workflow
        SetupBat[setupdev.bat] --> Venv[Create Python env]
        SetupBat --> Dep[pip install requirements.txt]
        SetupBat --> EnvCheck{Check .env}
        EnvCheck -- Missing --> CopyEnv[Copy .env.example to .env]
        EnvCheck -- Exists --> SkipEnv[Keep existing .env]
        SetupBat --> Migrate[alembic upgrade head]
        SetupBat --> NpmInst[cd frontend && npm install]
    end

    subgraph Run Workflow
        RunBat[runapplication.bat] --> BackendProc[Start FastAPI on :8000]
        RunBat --> FrontendProc[Start Vite React on :3000]
    end
```

- **`setupdev.bat`**: Bootstraps the entire project from a clean clone without manual configuration.
- **`runapplication.bat`**: Launches the FastAPI backend and Vite frontend dev servers in independent command windows.
- **`pytest -v`**: Executes all 42 automated tests covering CRUD, deduplication, sign convention, AI categorization, and SDK tests.
