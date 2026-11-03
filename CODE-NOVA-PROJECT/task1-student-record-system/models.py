"""Student model and input validation."""
import re
from dataclasses import dataclass, asdict

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_roll_no(value: str) -> str:
    value = str(value).strip()
    if not value:
        raise ValidationError("Roll number cannot be empty.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValidationError("Roll number may contain only letters, digits, '-' and '_'.")
    return value.upper()


def validate_name(value: str) -> str:
    value = " ".join(str(value).split())
    if len(value) < 2 or not re.fullmatch(r"[A-Za-z .'-]+", value):
        raise ValidationError("Name must be at least 2 letters (letters, spaces, . ' - only).")
    return value


def validate_email(value: str) -> str:
    value = str(value).strip().lower()
    if not EMAIL_RE.match(value):
        raise ValidationError("Invalid email format (example: name@example.com).")
    return value


def validate_gpa(value) -> float:
    try:
        gpa = float(value)
    except (TypeError, ValueError):
        raise ValidationError("GPA must be a number.")
    if not 0.0 <= gpa <= 10.0:
        raise ValidationError("GPA must be between 0.0 and 10.0.")
    return round(gpa, 2)


@dataclass
class Student:
    roll_no: str
    name: str
    email: str
    gpa: float
    course: str = ""

    @classmethod
    def create(cls, roll_no, name, email, gpa, course=""):
        return cls(
            validate_roll_no(roll_no),
            validate_name(name),
            validate_email(email),
            validate_gpa(gpa),
            " ".join(str(course).split()),
        )

    def to_dict(self):
        return asdict(self)
