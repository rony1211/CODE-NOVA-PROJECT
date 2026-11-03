"""Generates sample_transactions.json (run: python make_sample_data.py)."""
from expense_tracker import ExpenseTracker
import os
if os.path.exists("sample_transactions.json"):
    os.remove("sample_transactions.json")
t = ExpenseTracker("sample_transactions.json")
rows = [
    ("2026-10-01", "income", "Salary", "25000.00", "Monthly stipend"),
    ("2026-10-02", "expense", "Food", "350.50", "Groceries"),
    ("2026-10-04", "expense", "Utilities", "899.00", "Electricity bill"),
    ("2026-10-06", "expense", "Travel", "1200.00", "Train tickets"),
    ("2026-10-09", "expense", "Entertainment", "499.00", "OTT subscription"),
    ("2026-10-12", "expense", "Education", "1500.00", "Online course"),
    ("2026-10-15", "income", "Other", "2000.00", "Freelance project"),
    ("2026-10-18", "expense", "Food", "620.75", "Dining out"),
    ("2026-10-22", "expense", "Health", "450.00", "Pharmacy"),
    ("2026-10-27", "expense", "Shopping", "2299.99", "Headphones"),
]
for r in rows:
    t.add(*r)
print("Created sample_transactions.json with", len(rows), "records")
