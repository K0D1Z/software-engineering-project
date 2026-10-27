from dataclasses import dataclass
from decimal import Decimal
from .striped_type import StripedType

_MAX_DIGITS = 18
_DECIMAL_PLACES = 2

@dataclass(frozen=True)
class MoneyAmount(StripedType):
    amount: Decimal

    def value(self) -> Decimal:
        return self.amount

    def validate(self):
        if not isinstance(self.amount, Decimal):
            raise TypeError("Money amount must be a Decimal")
        if not self.amount.is_finite():
            raise ValueError("Money amount must be a finite number")
        if self.amount <= 0:
            raise ValueError("Money amount must be greater than zero")
        exponent = self.amount.as_tuple().exponent
        if -exponent > _DECIMAL_PLACES and self.amount != self.amount.quantize(Decimal(1).scaleb(-_DECIMAL_PLACES)):
            raise ValueError(f"Money amount can have at most {_DECIMAL_PLACES} decimal places")
        if self.amount >= Decimal(10) ** (_MAX_DIGITS - _DECIMAL_PLACES):
            raise ValueError("Money amount is too large")
