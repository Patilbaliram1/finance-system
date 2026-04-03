"""
Seed script — populates the database with sample users and transactions.
Run: python seed.py
"""

from database import SessionLocal, engine
import models
from auth import hash_password
from datetime import date

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data
db.query(models.Transaction).delete()
db.query(models.User).delete()
db.commit()

# Create Users
admin = models.User(
    username="admin",
    email="admin@finance.com",
    hashed_password=hash_password("admin123"),
    role="admin",
)
analyst = models.User(
    username="analyst",
    email="analyst@finance.com",
    hashed_password=hash_password("analyst123"),
    role="analyst",
)
viewer = models.User(
    username="viewer",
    email="viewer@finance.com",
    hashed_password=hash_password("viewer123"),
    role="viewer",
)
db.add_all([admin, analyst, viewer])
db.commit()
db.refresh(admin)
db.refresh(analyst)

# Create Transactions
transactions = [
    models.Transaction(amount=5000.00, type="income",  category="Salary",    date=date(2025, 1, 1),  notes="January salary",      user_id=admin.id),
    models.Transaction(amount=1200.00, type="expense", category="Rent",      date=date(2025, 1, 5),  notes="Monthly rent",         user_id=admin.id),
    models.Transaction(amount=300.00,  type="expense", category="Groceries", date=date(2025, 1, 10), notes="Weekly groceries",     user_id=admin.id),
    models.Transaction(amount=5000.00, type="income",  category="Salary",    date=date(2025, 2, 1),  notes="February salary",      user_id=admin.id),
    models.Transaction(amount=150.00,  type="expense", category="Utilities", date=date(2025, 2, 7),  notes="Electricity bill",     user_id=admin.id),
    models.Transaction(amount=800.00,  type="expense", category="Shopping",  date=date(2025, 2, 14), notes="Valentine's gift",     user_id=admin.id),
    models.Transaction(amount=5000.00, type="income",  category="Salary",    date=date(2025, 3, 1),  notes="March salary",         user_id=admin.id),
    models.Transaction(amount=200.00,  type="income",  category="Freelance", date=date(2025, 3, 15), notes="Logo design project",  user_id=admin.id),
    models.Transaction(amount=500.00,  type="expense", category="Travel",    date=date(2025, 3, 20), notes="Weekend trip",         user_id=admin.id),
    models.Transaction(amount=250.00,  type="expense", category="Dining",    date=date(2025, 3, 25), notes="Dinner with friends",  user_id=admin.id),

    models.Transaction(amount=3500.00, type="income",  category="Salary",    date=date(2025, 1, 1),  notes="January salary",       user_id=analyst.id),
    models.Transaction(amount=900.00,  type="expense", category="Rent",      date=date(2025, 1, 3),  notes="Monthly rent",         user_id=analyst.id),
    models.Transaction(amount=120.00,  type="expense", category="Groceries", date=date(2025, 1, 12), notes="Supermarket",          user_id=analyst.id),
    models.Transaction(amount=3500.00, type="income",  category="Salary",    date=date(2025, 2, 1),  notes="February salary",      user_id=analyst.id),
    models.Transaction(amount=400.00,  type="expense", category="Health",    date=date(2025, 2, 20), notes="Doctor visit + meds",  user_id=analyst.id),
]

db.add_all(transactions)
db.commit()
db.close()

print("✅ Seed complete!")
print("\nTest Accounts:")
print("  Admin    → username: admin,   password: admin123")
print("  Analyst  → username: analyst, password: analyst123")
print("  Viewer   → username: viewer,  password: viewer123")
print("\nStart the server: python app.py")
print("API running at:   http://127.0.0.1:5000")
