"""Функции приведения значений Excel к типам доменной модели."""

from datetime import date
from typing import Any

from pandas import isna, to_datetime

from .normalizers import normalize_float, normalize_str


def convert(value: Any, target_type: Any) -> Any | None:
    """Преобразует сырое значение Excel к целевому Python-типу."""
    if isna(value) or value == "":
        return None

    if isinstance(value, target_type) and target_type in (str, int, float, bool):
        return value

    if target_type is str:
        return normalize_str(value)

    if target_type is int:
        return int(normalize_float(value))

    if target_type is float:
        return normalize_float(value)

    if target_type is bool:
        return _convert_to_bool(value)

    if target_type is date:
        converted = to_datetime(value, errors="coerce")
        if isna(converted):
            return None
        return converted.date()

    return value


def _convert_to_bool(value: Any) -> bool:
    """Преобразует строковые и числовые признаки в булево значение."""
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    normalized = normalize_str(value).lower()

    if normalized in {"1", "true", "yes", "y", "да"}:
        return True

    if normalized in {"0", "false", "no", "n", "нет"}:
        return False

    raise ValueError(f"Cannot convert value {value!r} to bool")
