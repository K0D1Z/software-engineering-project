from dataclasses import dataclass
from .striped_type import StripedType

@dataclass(frozen=True)
class ClientNumber(StripedType):
    number: str

    def value(self) -> str:
        return self.number

    def validate(self):
        if not self.number:
            raise ValueError("Client number can not be empty")
        if not self.number.isascii() or not self.number.isdigit():
            raise ValueError("Client number must contain only digits")
        if len(self.number)!=8:
            raise ValueError("Client number is incorrect")