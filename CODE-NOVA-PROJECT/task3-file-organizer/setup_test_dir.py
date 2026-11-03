"""Creates a messy test folder (including duplicate names) for safe testing."""
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "test_folder")
root.mkdir(exist_ok=True)
files = ["photo.jpg", "logo.PNG", "resume.pdf", "notes.txt", "backup.zip", "song.mp3",
         "movie.mp4", "script.py", "index.html", "data.csv", "unknown.xyz", "README"]
for name in files:
    (root / name).write_text(f"sample content of {name}")
(root / "old_folder").mkdir(exist_ok=True)
(root / "old_folder" / "keep_me.txt").write_text("subfolders are left untouched")
print(f"Created test folder: {root.resolve()}")
