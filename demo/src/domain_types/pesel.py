from dataclasses import dataclass
from .striped_type import StripedType

_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)

@dataclass(frozen=True)
class Pesel(StripedType):
    pesel: str

    def value(self) -> str:
        return self.pesel

    def validate(self):
        if not self.pesel:
            raise ValueError("Pesel must not be empty")

        if len(self.pesel)!=11:
            raise ValueError("Inccorect pesel lenght")

        if not self.pesel.isascii() or not self.pesel.isdigit():
            raise ValueError("Pesel must contain only digits")

        if not self.has_valid_checksum():
            raise ValueError("Incorrect pesel checksum")

    def has_valid_checksum(self) -> bool:
        digits = [int(c) for c in self.pesel]
        total = sum(d * w for d, w in zip(digits[:10], _WEIGHTS))
        return (10 - total % 10) % 10 == digits[10]
