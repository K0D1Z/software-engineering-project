from dataclasses import dataclass
from .striped_type import StripedType

@dataclass(frozen=True)
class AccountNumber(StripedType):
    number: str

    def value(self) -> str:
        return self.number

    def validate(self):
        if not self.number:
            raise ValueError("Accont number can not be empty")
        if not self.number.isascii() or not self.number.isdigit():
            raise ValueError("Account number must contain only digits")
        if len(self.number)!=26:
            raise ValueError("Account number is incorrect")