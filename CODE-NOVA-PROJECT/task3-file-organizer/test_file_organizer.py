import tempfile, unittest
from pathlib import Path
import file_organizer as fo


class T(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        for n in ["a.jpg", "b.pdf", "c.zip", "d.mp3", "e.py", "f.xyz"]:
            (self.d / n).write_text(n)
        (self.d / "sub").mkdir()

    def test_dry_run_changes_nothing(self):
        before = sorted(p.name for p in self.d.iterdir())
        fo.main([str(self.d), "--dry-run", "--log", str(self.d.parent / "l.log")])
        self.assertEqual(before, sorted(p.name for p in self.d.iterdir()))

    def test_live_moves(self):
        fo.main([str(self.d), "--log", str(self.d.parent / "l.log")])
        self.assertTrue((self.d / "Images" / "a.jpg").exists())
        self.assertTrue((self.d / "Code" / "e.py").exists())
        self.assertTrue((self.d / "Others" / "f.xyz").exists())
        self.assertTrue((self.d / "sub").is_dir())

    def test_duplicates_preserved(self):
        (self.d / "Images").mkdir()
        (self.d / "Images" / "a.jpg").write_text("ORIGINAL")
        fo.main([str(self.d), "--log", str(self.d.parent / "l.log")])
        self.assertEqual((self.d / "Images" / "a.jpg").read_text(), "ORIGINAL")
        self.assertEqual((self.d / "Images" / "a_1.jpg").read_text(), "a.jpg")

    def test_invalid_dir(self):
        self.assertEqual(fo.main(["/no/such/dir", "--log", str(self.d.parent / "l.log")]), 1)


if __name__ == "__main__":
    unittest.main()
