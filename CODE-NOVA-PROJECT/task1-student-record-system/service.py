"""Business logic: CRUD operations on students."""
from models import Student, ValidationError, validate_roll_no, validate_name, validate_email, validate_gpa


class DuplicateIDError(Exception):
    pass


class NotFoundError(Exception):
    pass


class StudentService:
    def __init__(self, storage):
        self.storage = storage
        self.students = [Student(**r) for r in self._safe_records(storage.load())]

    @staticmethod
    def _safe_records(records):
        good = []
        for r in records:
            try:
                Student.create(**r)
                good.append(Student.create(**r).to_dict())
            except (TypeError, ValidationError):
                print(f"[WARNING] Skipping invalid record: {r}")
        return good

    def _persist(self):
        self.storage.save([s.to_dict() for s in self.students])

    def _find(self, roll_no):
        roll_no = validate_roll_no(roll_no)
        for s in self.students:
            if s.roll_no == roll_no:
                return s
        raise NotFoundError(f"No student with roll number {roll_no}.")

    def add(self, roll_no, name, email, gpa, course=""):
        student = Student.create(roll_no, name, email, gpa, course)
        if any(s.roll_no == student.roll_no for s in self.students):
            raise DuplicateIDError(f"Roll number {student.roll_no} already exists.")
        self.students.append(student)
        self._persist()
        return student

    def all(self):
        return sorted(self.students, key=lambda s: s.roll_no)

    def search(self, query):
        """Case-insensitive partial match on roll number or name."""
        q = query.strip().lower()
        if not q:
            raise ValidationError("Search query cannot be empty.")
        return [s for s in self.all() if q in s.roll_no.lower() or q in s.name.lower()]

    def update(self, roll_no, **fields):
        student = self._find(roll_no)
        validators = {"name": validate_name, "email": validate_email, "gpa": validate_gpa}
        for key, value in fields.items():
            if value in (None, ""):
                continue
            if key == "course":
                student.course = " ".join(str(value).split())
            elif key in validators:
                setattr(student, key, validators[key](value))
            else:
                raise ValidationError(f"Cannot update field '{key}'.")
        self._persist()
        return student

    def delete(self, roll_no):
        student = self._find(roll_no)
        self.students.remove(student)
        self._persist()
        return student
