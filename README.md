# Finance Tracking System — Python Backend

A RESTful backend API for managing personal financial records, built with **Flask**, **SQLAlchemy**, and **SQLite**.

---

## Tech Stack

| Layer       | Technology                  |
|-------------|----------------------------|
| Framework   | Flask                       |
| Database    | SQLite (via SQLAlchemy ORM) |
| Auth        | JWT (python-jose + bcrypt)  |
| Server      | Flask built-in (dev)        |

---

## Project Structure

```
finance_system/
├── app.py                      # App entry point, Blueprint registration
├── database.py                 # DB engine, session, Base
├── models.py                   # SQLAlchemy ORM models (User, Transaction)
├── auth.py                     # JWT auth, password hashing, role decorators
├── seed.py                     # Seed script for test data
├── requirements.txt
├── routers/
│   ├── users.py                # Register, login, user management
│   ├── transactions.py         # CRUD + filtering for transactions
│   └── analytics.py            # Summary and analytics endpoints
└── README.md
```

---

## Setup & Run

### 1. Extract / clone the project

```bash
cd finance_system
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Seed the database

```bash
python seed.py
```

### 5. Start the server

```bash
python app.py
```

API is now running at: **http://127.0.0.1:5000**

---

## User Roles

| Role     | Permissions                                              |
|----------|----------------------------------------------------------|
| `viewer`   | View own transactions and summary                      |
| `analyst`  | View + create + update transactions, access analytics  |
| `admin`    | Full access — manage all users and transactions        |

---

## API Endpoints

### Auth / Users

| Method | Endpoint          | Role   | Description              |
|--------|-------------------|--------|--------------------------|
| POST   | `/users/register` | Public | Register a new user      |
| POST   | `/users/login`    | Public | Login, receive JWT token |
| GET    | `/users/me`       | Any    | Get current user profile |
| GET    | `/users/`         | Admin  | List all users           |
| DELETE | `/users/<id>`     | Admin  | Delete a user            |

### Transactions

| Method | Endpoint                | Role           | Description                    |
|--------|-------------------------|----------------|--------------------------------|
| POST   | `/transactions/`        | Analyst, Admin | Create a transaction           |
| GET    | `/transactions/`        | Any            | List with optional filters     |
| GET    | `/transactions/<id>`    | Any            | Get single transaction         |
| PUT    | `/transactions/<id>`    | Analyst, Admin | Update a transaction           |
| DELETE | `/transactions/<id>`    | Admin          | Delete a transaction           |

#### Filter Parameters for `GET /transactions/`
- `type` — `income` or `expense`
- `category` — partial match
- `start_date` — format: `YYYY-MM-DD`
- `end_date` — format: `YYYY-MM-DD`
- `skip` — pagination offset (default 0)
- `limit` — max results (default 50, max 200)

### Analytics

| Method | Endpoint              | Role | Description             |
|--------|-----------------------|------|-------------------------|
| GET    | `/analytics/summary`  | Any  | Full financial summary  |

**Summary response includes:**
- Total income, total expenses, current balance
- Category-wise breakdown
- Monthly totals (income, expense, balance per month)
- Recent 5 transactions

---

## How to Test

### Using curl or Postman

```bash
# 1. Register a user
curl -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@test.com","password":"pass123","role":"analyst"}'

# 2. Login and get token
curl -X POST http://localhost:5000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123"}'

# 3. Use token in requests
curl http://localhost:5000/transactions/ \
  -H "Authorization: Bearer <your_token>"

# 4. Get financial summary
curl http://localhost:5000/analytics/summary \
  -H "Authorization: Bearer <your_token>"

# 5. Filter transactions
curl "http://localhost:5000/transactions/?type=income&start_date=2025-01-01&end_date=2025-03-31" \
  -H "Authorization: Bearer <your_token>"
```

### Seeded Test Accounts

| Username | Password    | Role     |
|----------|-------------|----------|
| admin    | admin123    | admin    |
| analyst  | analyst123  | analyst  |
| viewer   | viewer123   | viewer   |

---

## Assumptions Made

1. Transactions belong to a user — viewers and analysts see only their own; admins see all.
2. Analysts can create and update but not delete transactions (admin-only to prevent accidental data loss).
3. SQLite is used for simplicity — switching to PostgreSQL requires only changing `DATABASE_URL` in `database.py`.
4. JWT tokens expire after 60 minutes.
5. Amount must always be positive — the `type` field determines income vs expense.

---

## Design Decisions

- **Flask Blueprints** for clean separation of routes (users, transactions, analytics).
- **Role-based decorators** (`@login_required`, `@role_required`) in `auth.py` — reusable across all routes.
- **SQLAlchemy ORM** for clean, Pythonic database access.
- **`to_dict()` methods** on models for consistent JSON serialization.
- **Separation of concerns** — routing logic in `routers/`, DB models in `models.py`, auth in `auth.py`.
