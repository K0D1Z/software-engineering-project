import re
from dataclasses import dataclass, field
from .striped_type import StripedType

_EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,}"
)

@dataclass(frozen=True)
class Email(StripedType):
    email: str

    def value(self) -> str:
        return self.email

    def validate(self):
        if not self.email:
            raise ValueError("E-mail must not be empty")

        if not _EMAIL_RE.fullmatch(self.email):
            raise ValueError("Wrong e-mail format")
