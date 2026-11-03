"""JSON persistence layer (kept separate from business logic)."""
import json
import os
import shutil
import tempfile


class StorageError(Exception):
    pass


class JsonStorage:
    def __init__(self, path="students.json"):
        self.path = path

    def load(self):
        """Return list of dicts. Corrupted files are backed up, not crashed on."""
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Top-level JSON must be a list.")
            return data
        except (json.JSONDecodeError, ValueError) as exc:
            backup = self.path + ".corrupt.bak"
            shutil.copy(self.path, backup)
            print(f"[WARNING] Data file corrupted ({exc}). Backup saved to {backup}. Starting empty.")
            return []
        except OSError as exc:
            raise StorageError(f"Cannot read {self.path}: {exc}")

    def save(self, records):
        """Atomic write: write temp file then replace, so a crash never corrupts data."""
        directory = os.path.dirname(os.path.abspath(self.path))
        try:
            fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            os.replace(tmp, self.path)
        except OSError as exc:
            raise StorageError(f"Cannot write {self.path}: {exc}")
