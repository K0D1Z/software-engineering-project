import re
from dataclasses import dataclass, field
from .striped_type import StripedType

_POSTAL_CODE_RE = re.compile(r"[0-9]{2}-[0-9]{3}")

@dataclass(frozen=True)
class PostalCode(StripedType):
    code: str
    verify: bool = field(default=False)

    def value(self) -> str:
        return self.code

    def validate(self):
        if not self.code:
            raise ValueError("Postal code must not be empty")

        if not self.verify:
            return

        if not _POSTAL_CODE_RE.fullmatch(self.code):
            raise ValueError("Postal code must have format NN-NNN")
