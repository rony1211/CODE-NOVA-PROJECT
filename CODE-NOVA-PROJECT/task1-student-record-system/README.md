# Task 1 — Student Record Management System

A command-line CRUD application for managing student records with persistent JSON storage.

## Features
- Add, view, search, update and delete students
- Case-insensitive **partial** search by roll number or name
- Validation: unique roll numbers, email format, GPA range (0–10), name format
- Atomic JSON saves; corrupted data files are backed up (`.corrupt.bak`) instead of crashing
- Clean separation: `models.py` (validation) · `storage.py` (persistence) · `service.py` (logic) · `main.py` (CLI)

## Tech stack
Python 3, `json`, `dataclasses`, `unittest`

## Setup & run
```bash
python main.py                 # uses students.json (pre-populated sample data)
python main.py my_data.json    # use another data file
python test_student_system.py  # run tests
```

## Screenshots
Add terminal screenshots here (add / view / search / error handling).

![screenshot](screenshots/run.png)

## Error handling
Invalid input, duplicate IDs, missing records, corrupted/unwritable files all show a friendly message and never terminate the program.
