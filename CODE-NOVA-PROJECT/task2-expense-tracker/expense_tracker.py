"""Expense Tracker - income/expense logging, balances, filtering, CSV/JSON export."""
import csv
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CATEGORIES = ["Food", "Utilities", "Travel", "Shopping", "Health", "Education", "Entertainment", "Salary", "Other"]
TYPES = ("income", "expense")


class ValidationError(ValueError):
    pass


def parse_date(text: str) -> date:
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        raise ValidationError("Date must be in YYYY-MM-DD format (e.g. 2026-10-25).")


def parse_amount(text) -> Decimal:
    try:
        amount = Decimal(str(text).strip()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValidationError("Amount must be a number.")
    if not amount.is_finite() or amount <= 0:
        raise ValidationError("Amount must be greater than zero (negative amounts are rejected).")
    return amount


def parse_category(text: str) -> str:
    cat = text.strip().title()
    if cat not in CATEGORIES:
        raise ValidationError(f"Category must be one of: {', '.join(CATEGORIES)}.")
    return cat


def parse_type(text: str) -> str:
    t = text.strip().lower()
    if t not in TYPES:
        raise ValidationError("Type must be 'income' or 'expense'.")
    return t


@dataclass
class Transaction:
    date: str
    type: str
    category: str
    amount: str  # stored as string to keep Decimal precision in JSON
    description: str = ""


class ExpenseTracker:
    def __init__(self, path="transactions.json"):
        self.path = path
        self.transactions = []
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                self.transactions = [Transaction(**t) for t in json.load(f)]
        except (json.JSONDecodeError, TypeError, OSError) as exc:
            print(f"[WARNING] Could not read {self.path} ({exc}). Starting empty.")
            self.transactions = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.transactions], f, indent=2)

    def add(self, date_text, type_text, category_text, amount_text, description=""):
        t = Transaction(
            parse_date(date_text).isoformat(),
            parse_type(type_text),
            parse_category(category_text),
            str(parse_amount(amount_text)),
            description.strip(),
        )
        self.transactions.append(t)
        self.save()
        return t

    def filter(self, start=None, end=None, category=None, type_=None):
        s = parse_date(start) if start else None
        e = parse_date(end) if end else None
        if s and e and s > e:
            raise ValidationError("Start date must not be after end date.")
        cat = parse_category(category) if category else None
        result = []
        for t in self.transactions:
            d = date.fromisoformat(t.date)
            if s and d < s:
                continue
            if e and d > e:
                continue
            if cat and t.category != cat:
                continue
            if type_ and t.type != type_:
                continue
            result.append(t)
        return sorted(result, key=lambda t: t.date)

    @staticmethod
    def summary(transactions):
        income = sum((Decimal(t.amount) for t in transactions if t.type == "income"), Decimal("0"))
        expense = sum((Decimal(t.amount) for t in transactions if t.type == "expense"), Decimal("0"))
        by_cat = defaultdict(Decimal)
        for t in transactions:
            if t.type == "expense":
                by_cat[t.category] += Decimal(t.amount)
        return {"income": income, "expense": expense, "balance": income - expense, "by_category": dict(by_cat)}

    def export_csv(self, path, transactions=None):
        rows = self.transactions if transactions is None else transactions
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "type", "category", "amount", "description"])
            for t in rows:
                w.writerow([t.date, t.type, t.category, t.amount, t.description])
        return path

    def export_json(self, path, transactions=None):
        rows = self.transactions if transactions is None else transactions
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in rows], f, indent=2)
        return path


def print_transactions(rows):
    if not rows:
        print("No transactions found.")
        return
    print(f"\n{'Date':<12}{'Type':<9}{'Category':<15}{'Amount':>10}  Description")
    print("-" * 70)
    for t in rows:
        print(f"{t.date:<12}{t.type:<9}{t.category:<15}{t.amount:>10}  {t.description}")


def print_summary(rows):
    s = ExpenseTracker.summary(rows)
    print("\n----- SUMMARY -----")
    print(f"Total income  : {s['income']:>12}")
    print(f"Total expense : {s['expense']:>12}")
    print(f"Net balance   : {s['balance']:>12}")
    if s["by_category"]:
        print("\nExpenses by category:")
        for cat, amt in sorted(s["by_category"].items(), key=lambda x: -x[1]):
            print(f"  {cat:<15}{amt:>10}")


def plot_expenses(rows):
    """Optional pie chart (needs matplotlib)."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib")
        return
    data = ExpenseTracker.summary(rows)["by_category"]
    if not data:
        print("No expenses to plot.")
        return
    plt.pie([float(v) for v in data.values()], labels=data.keys(), autopct="%1.1f%%")
    plt.title("Expenses by Category")
    plt.show()


MENU = """
=========== Expense Tracker ===========
 1. Add transaction      5. Export CSV
 2. View all             6. Export JSON
 3. Filter (date/category) 7. Plot chart (optional)
 4. Summary / balance    8. Exit
=======================================
"""


def run(tracker):
    while True:
        print(MENU)
        choice = input("Choose (1-8): ").strip()
        try:
            if choice == "1":
                t = tracker.add(input("Date (YYYY-MM-DD): "), input("Type (income/expense): "),
                                input(f"Category ({', '.join(CATEGORIES)}): "), input("Amount: "),
                                input("Description: "))
                print(f"Saved: {t.type} {t.amount} on {t.date}")
            elif choice == "2":
                print_transactions(tracker.filter())
            elif choice in ("3", "5", "6", "7"):
                rows = tracker.transactions
                if choice == "3" or input("Apply a filter first? (y/n): ").lower() == "y":
                    rows = tracker.filter(input("Start date (blank=any): ") or None,
                                          input("End date (blank=any): ") or None,
                                          input("Category (blank=any): ") or None)
                if choice == "3":
                    print_transactions(rows)
                    print_summary(rows)
                elif choice == "5":
                    print("Exported to", tracker.export_csv(input("File name [report.csv]: ") or "report.csv", rows))
                elif choice == "6":
                    print("Exported to", tracker.export_json(input("File name [report.json]: ") or "report.json", rows))
                else:
                    plot_expenses(rows)
            elif choice == "4":
                print_summary(tracker.transactions)
            elif choice == "8":
                print("Goodbye!")
                return
            else:
                print("Please enter 1-8.")
        except ValidationError as exc:
            print(f"[ERROR] {exc}")
        except OSError as exc:
            print(f"[FILE ERROR] {exc}")


if __name__ == "__main__":
    tracker = ExpenseTracker(sys.argv[1] if len(sys.argv) > 1 else "transactions.json")
    try:
        run(tracker)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
