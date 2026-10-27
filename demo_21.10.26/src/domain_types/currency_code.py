import re
from dataclasses import dataclass
from .striped_type import StripedType

_CURRENCY_CODE_RE = re.compile(
    r"^[A-Z]{3}$"
)

@dataclass(frozen=True)
class CurrencyCode(StripedType):
    code: str

    def value(self) -> str:
        return self.code

    def validate(self):
        if not self.code:
            raise ValueError("Currency code can not be empty")
        if not _CURRENCY_CODE_RE.fullmatch(self.code):
            raise ValueError("Invalid currency code")

    
    