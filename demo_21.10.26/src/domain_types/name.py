import re
from dataclasses import dataclass
from .striped_type import StripedType

_MAX_LENGTH = 100
_NAME_RE = re.compile(r"[^\W\d_]+(?:[ '\-][^\W\d_]+)*")

@dataclass(frozen=True)
class Name(StripedType):
    name: str

    def value(self) -> str:
        return self.name

    def validate(self):
        if not self.name:
            raise ValueError("Name must not be empty")

        if len(self.name) > _MAX_LENGTH:
            raise ValueError(f"Name must be at most {_MAX_LENGTH} characters long")

        if not _NAME_RE.fullmatch(self.name):
            raise ValueError("Name must contain only letters, spaces, hyphens and apostrophes")
