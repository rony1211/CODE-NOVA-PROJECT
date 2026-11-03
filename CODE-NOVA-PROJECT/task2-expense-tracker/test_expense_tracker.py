import os, tempfile, unittest
from decimal import Decimal
from expense_tracker import ExpenseTracker, ValidationError


class T(unittest.TestCase):
    def setUp(self):
        self.tr = ExpenseTracker(os.path.join(tempfile.mkdtemp(), "t.json"))
        self.tr.add("2026-10-01", "income", "Salary", "1000.10")
        self.tr.add("2026-10-05", "expense", "Food", "0.10")
        self.tr.add("2026-10-05", "expense", "Food", "0.20")
        self.tr.add("2026-11-01", "expense", "Travel", "100")

    def test_precision(self):
        s = self.tr.summary(self.tr.transactions)
        self.assertEqual(s["expense"], Decimal("100.30"))
        self.assertEqual(s["balance"], Decimal("899.80"))

    def test_date_filter(self):
        self.assertEqual(len(self.tr.filter("2026-10-01", "2026-10-31")), 3)
        self.assertEqual(len(self.tr.filter("2026-10-05", "2026-10-05")), 2)

    def test_category_filter(self):
        self.assertEqual(len(self.tr.filter(category="food")), 2)

    def test_rejects_bad_input(self):
        for args in [("2026-10-01", "expense", "Food", "-5"), ("2026-13-45", "expense", "Food", "5"),
                     ("2026-10-01", "expense", "Food", "abc"), ("2026-10-01", "spend", "Food", "5"),
                     ("2026-10-01", "expense", "Nope", "5"), ("2026-10-01", "expense", "Food", "0")]:
            with self.assertRaises(ValidationError):
                self.tr.add(*args)

    def test_persistence_and_export(self):
        again = ExpenseTracker(self.tr.path)
        self.assertEqual(len(again.transactions), 4)
        out = again.export_csv(os.path.join(tempfile.mkdtemp(), "o.csv"))
        self.assertEqual(len(open(out).read().strip().splitlines()), 5)


if __name__ == "__main__":
    unittest.main()
