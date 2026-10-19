from dataclasses import dataclass, fields

@dataclass(frozen=True)
class StripedType():
    def __post_init__(self):
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, str):
                object.__setattr__(self, f.name, value.strip())
        self.validate()