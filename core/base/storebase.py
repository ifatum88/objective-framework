"""Базовая реализация store-объектов проекта."""

from dataclasses import MISSING, fields
from pathlib import Path
from typing import Any

from pandas import DataFrame, isna

from ..func import convert, loader_from_excel, normalize_column_name, normalize_str
from ..meta import Entity, QueryList


class StoreBase:
    """Базовый класс для загрузки, нормализации и сериализации сущностей."""

    _entity: Any = None
    _raw_data: DataFrame | None = None
    _raw_items: QueryList | None = None

    items: QueryList | None = None
    
    def __init__(self, entity: Any):
        """Инициализирует store для конкретного класса сущности."""
        if not isinstance(entity, type) or not issubclass(entity, Entity):
            raise TypeError(f"{entity!r} must be a class inheriting from Entity")
        self._entity = entity

    def load(self, excel_path: Path, **excel_kwargs):
        """Загружает Excel-файл и подготавливает сырые данные к нормализации."""

        self._reset_pipeline()

        data = loader_from_excel(excel_path, **excel_kwargs)
        data = data.rename(columns=normalize_column_name)
        self._raw_data = data
        self._raw_items = QueryList(data.to_dict("records"))

        return self
    
    def normalize(self, is_map: bool = False, lookups: dict[type[Entity], Any] | None = None):
        """Преобразует сырые строки в экземпляры целевой сущности."""

        self._ensure_loaded("normalize()")

        norm_items = []
        
        for item in self._raw_items:
            values = self._build_entity_values(item, is_map=is_map, lookups=lookups)
            norm_items.append(self._entity(**values))
            
        self.items = QueryList(norm_items)

        return self

    def map(self, lookups: dict[type[Entity], Any]):
        """Подменяет строковые ссылки на полноценные сущности справочников."""

        self._ensure_normalized("map()")

        mapped_items = []

        for item in self.items:
            values = {}

            for field in fields(self._entity):
                attr = field.name
                target_type = field.type
                value = getattr(item, attr)

                if not self._is_entity_type(target_type):
                    values[attr] = value
                    continue

                if isinstance(value, target_type):
                    values[attr] = value
                    continue

                lookup_items = self._get_lookup_items(target_type, lookups)
                values[attr] = self._find_lookup_entity(value, target_type, lookup_items)

            mapped_items.append(self._entity(**values))

        self.items = QueryList(mapped_items)

        return self

    def to_dataframe(self) -> DataFrame:
        """Возвращает содержимое store в виде pandas.DataFrame."""

        self._ensure_normalized("to_dataframe()")

        if len(self.items) == 0:
            return DataFrame(columns=self._entity.get_attrs())

        rows = [
            self._entity_to_export_dict(item)
            for item in self.items
        ]

        return DataFrame(rows)

    def export(self) -> DataFrame:
        """Возвращает экспортное представление данных."""
        return self.to_dataframe()

    def _reset_pipeline(self) -> None:
        """Сбрасывает состояния пайплайна перед новой загрузкой."""
        self._raw_data = None
        self._raw_items = None
        self.items = None

    def _ensure_loaded(self, operation: str) -> None:
        """Проверяет, что сырые данные уже были загружены."""
        if self._raw_items is None:
            raise RuntimeError(
                f"{self.__class__.__name__}.load() must be called before {operation}"
            )

    def _ensure_normalized(self, operation: str) -> None:
        """Проверяет, что нормализованные элементы уже подготовлены."""
        if self.items is None:
            raise RuntimeError(
                f"{self.__class__.__name__}.normalize() must be called before {operation}"
            )
        
    def _build_entity_values(
        self,
        item: dict[str, object],
        is_map: bool = False,
        lookups: dict[type[Entity], Any] | None = None,
    ) -> dict[str, object]:
        """Собирает словарь значений для создания экземпляра сущности."""

        values: dict[str, object] = {}
        missing_fields: list[str] = []
        lookups = lookups or {}

        for field in fields(self._entity):
            attr = field.name
            target_type = field.type
            is_entity_field = self._is_entity_type(target_type)

            if attr not in item:
                if self._is_required_field(field):
                    missing_fields.append(attr)
                continue

            raw_value = item[attr]

            if is_entity_field:
                values[attr] = self._resolve_lookup_field_value(
                    value=raw_value,
                    target_type=target_type,
                    is_map=is_map,
                    lookups=lookups,
                )
                continue

            if self._is_empty_value(raw_value):
                if self._is_required_field(field):
                    missing_fields.append(attr)
                continue
            
            converted_value = convert(raw_value, target_type)

            if converted_value is None:
                if self._is_required_field(field):
                    missing_fields.append(attr)
                continue

            values[attr] = converted_value

        if missing_fields:
            raise ValueError(
                f"Missing required fields for {self._entity.__name__}: {missing_fields}"
            )

        return values

    def _resolve_lookup_field_value(
        self,
        value: object,
        target_type: type[Entity],
        is_map: bool,
        lookups: dict[type[Entity], Any],
    ) -> object:
        """Преобразует ссылочное поле либо в строку, либо в сущность справочника."""

        if self._is_empty_value(value):
            if not is_map:
                return ""

            lookup_items = self._get_lookup_items(target_type, lookups)
            return self._find_lookup_entity("", target_type, lookup_items)

        if not is_map:
            return convert(value, str)

        lookup_items = self._get_lookup_items(target_type, lookups)
        return self._find_lookup_entity(value, target_type, lookup_items)

    def _get_lookup_items(
        self,
        target_type: type[Entity],
        lookups: dict[type[Entity], Any],
    ) -> QueryList:
        """Достаёт коллекцию элементов справочника по типу сущности."""
        lookup_store = lookups.get(target_type)

        if isinstance(lookup_store, QueryList):
            return lookup_store

        if lookup_store is None or getattr(lookup_store, "items", None) is None:
            raise ValueError(
                f"Lookup store for {target_type.__name__} is required"
            )

        return lookup_store.items

    def _find_lookup_entity(
        self,
        value: object,
        target_type: type[Entity],
        lookup_items: QueryList,
    ) -> Entity:
        """Ищет сущность в справочнике по lookup-полю или возвращает default."""
        for item in lookup_items:
            if self._lookup_values_equal(item.get_search_value(), value):
                return item

        for item in lookup_items:
            if item.is_default():
                return item

        raise LookupError(
            f"No lookup entity found for {target_type.__name__}: {value!r}"
        )

    def _entity_to_export_dict(self, item: Entity) -> dict[str, object]:
        """Преобразует сущность в словарь для дальнейшего экспорта."""
        row: dict[str, object] = {}

        for field in fields(self._entity):
            attr = field.name
            value = getattr(item, attr)

            if isinstance(value, Entity):
                row[attr] = value.to_export_value()
                continue

            row[attr] = value

        return row
    
    def _display_parts(self) -> dict[str, object]:
        return {
            "entity": self._entity.__name__, 
            "items": len(self.items) if self.items is not None else 0,
        }
    
    def __repr__(self) -> str:
        parts = ", ".join(
            f"{key}={value!r}"
            for key, value in self._display_parts().items()
        )
        return f"{self.__class__.__name__}({parts})"

    def __str__(self) -> str:
        parts = ", ".join(
            f"{key}={value}"
            for key, value in self._display_parts().items()
        )
        return f"{self.__class__.__name__}({parts})"


    @staticmethod
    def _is_empty_value(value: object) -> bool:
        """Определяет, считается ли значение пустым после чтения из Excel."""
        return value == "" or isna(value)

    @staticmethod
    def _is_required_field(field: Any) -> bool:
        """Проверяет, нужно ли поле обязательно передать в dataclass."""
        return field.default is MISSING and field.default_factory is MISSING

    @staticmethod
    def _is_entity_type(target_type: object) -> bool:
        """Проверяет, является ли тип поля ссылкой на другую сущность."""
        return isinstance(target_type, type) and issubclass(target_type, Entity)

    @staticmethod
    def _lookup_values_equal(left: object, right: object) -> bool:
        """Сравнивает lookup-значения с мягкой нормализацией строк."""
        if isinstance(left, str) and isinstance(right, str):
            return normalize_str(left) == normalize_str(right)

        return left == right
