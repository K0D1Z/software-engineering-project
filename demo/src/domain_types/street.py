import re
from dataclasses import dataclass
from striped_type import StripedType

_MAX_LENGTH = 100
_STREET_RE = re.compile(r"[^\W_]+(?:[ '.\-/][^\W_]+)*\.?")

@dataclass(frozen=True)
class Street(StripedType):
    street: str

    def value(self) -> str:
        return self.street

    def validate(self):
        if not self.street:
            raise ValueError("Street must not be empty")

        if len(self.street) > _MAX_LENGTH:
            raise ValueError(f"Street must be at most {_MAX_LENGTH} characters long")

        if not any(c.isalpha() for c in self.street):
            raise ValueError("Street must contain at least one letter")

        if not _STREET_RE.fullmatch(self.street):
            raise ValueError("Street must contain only letters, digits, spaces, hyphens, apostrophes, dots and slashes")
