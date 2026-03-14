"""Функции нормализации значений, прочитанных из Excel."""

from typing import Any


def normalize_column_name(column_name: str) -> str:
    """Приводит имя колонки Excel к внутреннему формату поля."""
    normalized = column_name.lower()
    normalized = normalized.replace(" ", "")
    normalized = normalized.replace(".", "_")
    return normalized


def normalize_str(value: str) -> str:
    """Очищает строку от неразрывных пробелов и лишних отступов."""
    return str(value).replace("\xa0", " ").strip()


def normalize_float(value: Any) -> float:
    """Преобразует текстовые числовые значения Excel в float."""
    if isinstance(value, (int, float)):
        return float(value)

    value_str = str(value).strip()
    value_str = value_str.replace("\xa0", "").replace(" ", "")
    value_str = value_str.replace(",", ".")

    return float(value_str)


# Алиасы оставлены для обратной совместимости со старым API.
normaliaze_column_name = normalize_column_name
normaliaze_str = normalize_str
