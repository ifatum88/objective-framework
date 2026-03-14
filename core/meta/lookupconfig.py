"""Служебные настройки lookup-поведения сущности."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LookupConfig:
    """Описывает поля поиска и экспорта для справочной сущности."""

    search_by: str
    export_field: str
