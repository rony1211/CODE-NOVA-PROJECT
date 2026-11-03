# Task 3 — Automated File Organizer

CLI tool that sorts files into `Images`, `Documents`, `Archives`, `Media`, `Code` and `Others` by extension.

## Features
- Choose source and target directory (argument or interactive prompt)
- **Dry-run mode** (`--dry-run`) lists every planned move without touching the disk
- **Safe duplicates**: existing files are never overwritten — new ones get `_1`, `_2`… suffixes
- Subfolders and symlinks are skipped; permission/locked-file errors are logged and skipped
- Action log written to `organizer.log`

## Usage
```bash
python setup_test_dir.py test_folder                 # create a messy test folder
python file_organizer.py test_folder --dry-run       # preview
python file_organizer.py test_folder                 # apply
python file_organizer.py test_folder -t sorted_out   # different target
python test_file_organizer.py                        # tests
```
See `execution_log_demo.txt` for a real dry-run vs. live-run comparison.

## Safety measures
1. Dry-run first. 2. Never overwrites. 3. Never deletes. 4. Only top-level files are moved. 5. Errors don't stop the run.

## Screenshots
![screenshot](screenshots/run.png)
