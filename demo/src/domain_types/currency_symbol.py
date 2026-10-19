from dataclasses import dataclass
from .striped_type import StripedType

_MAX_LENGTH = 5

@dataclass(frozen=True)
class CurrencySymbol(StripedType):
    symbol: str 

    def value(self) -> str:
        return self.symbol

    def validate(self):
        if not self.symbol:
            raise ValueError("Symbol must not be empty")
        if len(self.symbol) > _MAX_LENGTH:
            raise ValueError(f"Symbol must be at most {_MAX_LENGTH} characters long")