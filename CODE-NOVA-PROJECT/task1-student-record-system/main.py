"""Student Record Management System - interactive CLI."""
import sys
from models import ValidationError
from service import StudentService, DuplicateIDError, NotFoundError
from storage import JsonStorage, StorageError

MENU = """
========= Student Record Management =========
 1. Add student        4. Update student
 2. View all students  5. Delete student
 3. Search (ID/name)   6. Exit
=============================================
"""


def show(students):
    if not students:
        print("No records found.")
        return
    print(f"\n{'Roll No':<10}{'Name':<24}{'Email':<30}{'GPA':<6}Course")
    print("-" * 80)
    for s in students:
        print(f"{s.roll_no:<10}{s.name:<24}{s.email:<30}{s.gpa:<6}{s.course}")
    print(f"\nTotal: {len(students)}")


def ask(prompt):
    return input(prompt).strip()


def run(service):
    while True:
        print(MENU)
        choice = ask("Choose an option (1-6): ")
        try:
            if choice == "1":
                s = service.add(ask("Roll No: "), ask("Name: "), ask("Email: "), ask("GPA (0-10): "), ask("Course: "))
                print(f"Added {s.name} ({s.roll_no}).")
            elif choice == "2":
                show(service.all())
            elif choice == "3":
                show(service.search(ask("Search ID or name: ")))
            elif choice == "4":
                roll = ask("Roll No to update: ")
                print("Leave a field blank to keep current value.")
                s = service.update(roll, name=ask("New name: "), email=ask("New email: "),
                                   gpa=ask("New GPA: "), course=ask("New course: "))
                print(f"Updated {s.roll_no}.")
            elif choice == "5":
                roll = ask("Roll No to delete: ")
                if ask(f"Delete {roll}? (y/n): ").lower() == "y":
                    service.delete(roll)
                    print("Deleted.")
            elif choice == "6":
                print("Goodbye!")
                return
            else:
                print("Please enter a number from 1 to 6.")
        except (ValidationError, DuplicateIDError, NotFoundError) as exc:
            print(f"[ERROR] {exc}")
        except StorageError as exc:
            print(f"[STORAGE ERROR] {exc}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "students.json"
    try:
        run(StudentService(JsonStorage(path)))
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
