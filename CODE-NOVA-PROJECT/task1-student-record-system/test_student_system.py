import json, os, tempfile, unittest
from models import ValidationError
from service import StudentService, DuplicateIDError, NotFoundError
from storage import JsonStorage


class T(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "s.json")
        self.svc = StudentService(JsonStorage(self.path))

    def test_add_persist_restart(self):
        self.svc.add("c1", "Asha Rao", "asha@x.com", 8.5, "CSE")
        again = StudentService(JsonStorage(self.path))
        self.assertEqual(again.all()[0].roll_no, "C1")

    def test_duplicate(self):
        self.svc.add("c1", "Asha Rao", "asha@x.com", 8.5)
        with self.assertRaises(DuplicateIDError):
            self.svc.add("C1", "Other Person", "o@x.com", 7)

    def test_validation(self):
        for args in [("c2", "A", "a@x.com", 5), ("c2", "Ok Name", "bad-email", 5), ("c2", "Ok Name", "a@x.com", 11), ("c2", "Ok Name", "a@x.com", "abc")]:
            with self.assertRaises(ValidationError):
                self.svc.add(*args)

    def test_search_partial_case_insensitive(self):
        self.svc.add("c1", "Asha Rao", "asha@x.com", 8.5)
        self.assertEqual(len(self.svc.search("sHa")), 1)
        self.assertEqual(len(self.svc.search("c1")), 1)

    def test_update_delete(self):
        self.svc.add("c1", "Asha Rao", "asha@x.com", 8.5)
        self.svc.update("c1", gpa="9.0")
        self.assertEqual(self.svc.all()[0].gpa, 9.0)
        self.svc.delete("c1")
        with self.assertRaises(NotFoundError):
            self.svc.delete("c1")

    def test_corrupted_file(self):
        with open(self.path, "w") as f:
            f.write("{not json")
        svc = StudentService(JsonStorage(self.path))
        self.assertEqual(svc.all(), [])
        self.assertTrue(os.path.exists(self.path + ".corrupt.bak"))


if __name__ == "__main__":
    unittest.main()
