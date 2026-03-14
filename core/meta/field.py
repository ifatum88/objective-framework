"""Вспомогательное описание поля с типом и значением."""

from typing import Any, Type
from dataclasses import dataclass


@dataclass
class Field:
    """Универсальное typed-представление значения поля."""

    name: str
    data_type: Type[Any]
    value: Any | None = None
    default: Any | None = None

    def has_value(self) -> bool:
        return self.value is not None

    def is_default(self) -> bool:
        return self.value == self.default

    def get_value_or_default(self) -> Any:
        return self.value if self.value is not None else self.default

    def validate_type(self) -> bool:
        if self.value is None:
            return True
        return isinstance(self.value, self.data_type)

    def __repr__(self) -> str:
        return (
            f"Field("
            f"name={self.name!r}, "
            f"type={self.data_type.__name__}, "
            f"value={self.value!r}, "
            f"default={self.default!r}"
            f")"
        )

    def __str__(self) -> str:
        return f"{self.name}={self.value}"
