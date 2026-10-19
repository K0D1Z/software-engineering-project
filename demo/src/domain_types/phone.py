from dataclasses import dataclass
from striped_type import StripedType

@dataclass(frozen=True)
class Phone(StripedType):
    phone: str

    def value(self) -> str:
        return self.phone

    def validate(self):
        if not self.phone:
            raise ValueError("Phone number must not be empty")

        if not self.phone.isascii() or not self.phone.isdigit():
            raise ValueError("Phone number must contain only digits")