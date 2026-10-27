import re
from dataclasses import dataclass
from .striped_type import StripedType

_MAX_LENGTH = 100
_CITY_RE = re.compile(r"[^\W\d_]+(?:[ '.\-][^\W\d_]+)*\.?")

@dataclass(frozen=True)
class City(StripedType):
    city: str

    def value(self) -> str:
        return self.city

    def validate(self):
        if not self.city:
            raise ValueError("City must not be empty")

        if len(self.city) > _MAX_LENGTH:
            raise ValueError(f"City must be at most {_MAX_LENGTH} characters long")

        if not _CITY_RE.fullmatch(self.city):
            raise ValueError("City must contain only letters, spaces, hyphens, apostrophes and dots")
