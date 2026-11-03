#!/usr/bin/env python3
"""Automated File Organizer - sorts files into category folders by extension.

Examples:
    python file_organizer.py ~/Downloads --dry-run
    python file_organizer.py ~/Downloads --target ~/Sorted
"""
import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".csv", ".md", ".rtf"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Media": {".mp3", ".wav", ".flac", ".mp4", ".mkv", ".avi", ".mov", ".aac", ".webm"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".html", ".css", ".json", ".sh", ".go", ".rs", ".sql"},
}
OTHERS = "Others"


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return OTHERS


def unique_destination(dest: Path, reserved: set) -> Path:
    """Return a path that does not exist on disk or in this run's plan (adds _1, _2, ...)."""
    if not dest.exists() and dest not in reserved:
        return dest
    counter = 1
    while True:
        candidate = dest.with_name(f"{dest.stem}_{counter}{dest.suffix}")
        if not candidate.exists() and candidate not in reserved:
            return candidate
        counter += 1


def build_plan(source: Path, target: Path):
    """Create the list of (src, dest) moves without touching the disk. Subfolders are skipped."""
    plan, reserved, skipped = [], set(), []
    for item in sorted(source.iterdir()):
        try:
            if item.is_symlink() or not item.is_file():
                skipped.append(item)
                continue
        except PermissionError:
            skipped.append(item)
            continue
        dest = unique_destination(target / category_for(item) / item.name, reserved)
        reserved.add(dest)
        plan.append((item, dest))
    return plan, skipped


def execute_plan(plan, dry_run: bool):
    moved, failed = 0, []
    for src, dest in plan:
        label = f"{src.name}  ->  {dest.parent.name}/{dest.name}"
        if dry_run:
            print(f"[DRY-RUN] would move: {label}")
            continue
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            logging.info("MOVED %s -> %s", src, dest)
            print(f"[MOVED]   {label}")
            moved += 1
        except (PermissionError, OSError) as exc:  # locked file, read-only dir, etc.
            logging.error("FAILED %s: %s", src, exc)
            print(f"[FAILED]  {src.name}: {exc}")
            failed.append(src)
    return moved, failed


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Organize files into Images/Documents/Archives/Media/Code/Others folders.")
    p.add_argument("source", nargs="?", help="Directory to organize (prompted if omitted)")
    p.add_argument("-t", "--target", help="Destination directory (default: same as source)")
    p.add_argument("-n", "--dry-run", action="store_true", help="Preview planned moves without changing anything")
    p.add_argument("--log", default="organizer.log", help="Log file name (default: organizer.log)")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    source_text = args.source or input("Source directory to organize: ").strip()
    source = Path(source_text).expanduser().resolve()
    if not source.is_dir():
        print(f"[ERROR] '{source}' is not a valid directory.")
        return 1
    target = Path(args.target).expanduser().resolve() if args.target else source
    logging.basicConfig(filename=args.log, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Run started source=%s target=%s dry_run=%s", source, target, args.dry_run)

    try:
        plan, skipped = build_plan(source, target)
    except PermissionError as exc:
        print(f"[ERROR] Cannot read directory: {exc}")
        return 1

    mode = "DRY-RUN (no files will be changed)" if args.dry_run else "LIVE"
    print(f"\nMode: {mode}\nSource: {source}\nTarget: {target}\nFiles to organize: {len(plan)}\n")
    if not plan:
        print("Nothing to organize.")
        return 0
    moved, failed = execute_plan(plan, args.dry_run)
    print(f"\nSummary: {len(plan)} planned, {moved} moved, {len(failed)} failed, {len(skipped)} skipped (folders/links).")
    if args.dry_run:
        print("Re-run without --dry-run to apply these changes.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
