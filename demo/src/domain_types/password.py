from dataclasses import dataclass, field
from striped_type import StripedType
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


_MIN_LENGTH = 10
_MAX_LENGTH = 128

@dataclass(frozen=True)
class Password(StripedType):
    password: str

    def value(self) -> str:
        return self.password

    def validate(self):
        if not self.password:
            raise ValueError("Password must not be empty")

        if len(self.password) < _MIN_LENGTH:
            raise ValueError(f"Password must be at least {_MIN_LENGTH} characters long")

        if len(self.password) > _MAX_LENGTH:
            raise ValueError(f"Password must be at most {_MAX_LENGTH} characters long")

        if any(c.isspace() for c in self.password):
            raise ValueError("Password must not contain whitespace")

        if not any(c.islower() for c in self.password):
            raise ValueError("Password must contain a lowercase letter")

        if not any(c.isupper() for c in self.password):
            raise ValueError("Password must contain an uppercase letter")

        if not any(c.isdigit() for c in self.password):
            raise ValueError("Password must contain a digit")

        if not any(not c.isalnum() for c in self.password):
            raise ValueError("Password must contain a special character")

    def hash(self):
        ph = PasswordHasher()
        return ph.hash(password=self.password)