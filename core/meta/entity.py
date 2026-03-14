"""Базовый класс доменных сущностей."""

from dataclasses import fields, is_dataclass
from typing import Any, ClassVar

from .lookupconfig import LookupConfig


class Entity:
    """Базовый класс для dataclass-сущностей со служебным lookup-описанием."""

    __lookup__: ClassVar[LookupConfig | None] = None

    @classmethod
    def get_attrs(cls) -> list[str]:
        """Возвращает список полей dataclass-сущности."""
        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be a dataclass")
        return [f.name for f in fields(cls)]

    @classmethod
    def has_lookup(cls) -> bool:
        """Проверяет, описан ли для сущности lookup-конфиг."""
        return cls.__lookup__ is not None

    @classmethod
    def get_lookup_config(cls) -> LookupConfig:
        """Возвращает конфигурацию поиска и экспорта для сущности."""
        if cls.__lookup__ is None:
            raise AttributeError(f"{cls.__name__} has no lookup config")
        return cls.__lookup__

    @classmethod
    def get_search_field(cls) -> str:
        """Возвращает поле, по которому ищется сущность в справочнике."""
        return cls.get_lookup_config().search_by

    @classmethod
    def get_export_field(cls) -> str:
        """Возвращает поле, которое должно попасть в экспорт."""
        return cls.get_lookup_config().export_field
    
    def to_export_value(self) -> Any:
        """Возвращает значение поля, предназначенного для экспорта."""
        return getattr(self, self.get_export_field())

    def to_dict(self) -> dict[str, Any]:
        """Преобразует сущность в словарь всех её полей."""
        if not is_dataclass(self):
            raise TypeError(f"{self.__class__.__name__} must be a dataclass")
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def get_value(self, attr_name: str) -> Any:
        """Возвращает значение указанного поля сущности."""
        if attr_name not in self.get_attrs():
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{attr_name}'")
        return getattr(self, attr_name)
    
    def is_default(self) -> bool:
        """Проверяет, является ли сущность значением по умолчанию."""
        return getattr(self, "default", 0) == 1

    def get_search_value(self) -> Any:
        """Возвращает текущее значение lookup-поля экземпляра."""
        return getattr(self, self.get_search_field())

    def __repr__(self) -> str:
        if not is_dataclass(self):
            return super().__repr__()

        attrs = ", ".join(
            f"{f.name}={getattr(self, f.name)!r}"
            for f in fields(self)
        )
        return f"{self.__class__.__name__}({attrs})"

    def __str__(self) -> str:
        if not is_dataclass(self):
            return super().__str__()

        attrs = ", ".join(
            f"{f.name}={getattr(self, f.name)}"
            for f in fields(self)
        )
        return f"{self.__class__.__name__}({attrs})"
