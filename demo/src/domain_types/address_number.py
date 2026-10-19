from dataclasses import dataclass
from .striped_type import StripedType

@dataclass(frozen=True)
class AddressNumber(StripedType):
    number: str

    def value(self) -> str:
        return self.number

    def validate(self):
        if not self.number:
            raise ValueError("Addres number can not be empty")
        if not self.number.isascii() or not self.number.isdigit():
            raise ValueError("Addres number must contain only digits")
        if int(self.number)<0:
            raise ValueError("Addres number can not be negative")