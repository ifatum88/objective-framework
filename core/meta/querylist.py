from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class QueryList(Generic[T]):
    """Лёгкий list-подобный контейнер, используемый во framework-слое."""

    def __init__(self, items: T | Iterable[T] | None = None) -> None:
        self._items: list[T] = []

        if items is None:
            return

        if self._is_multi_value(items):
            self._items.extend(items)
            return

        self._items.append(items)

    @staticmethod
    def _is_multi_value(value: object) -> bool:
        return isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray))

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __setitem__(self, index: int, value: T) -> None:
        self._items[index] = value

    def __delitem__(self, index: int) -> None:
        del self._items[index]

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __str__(self) -> str:
        return str(self._items)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._items!r})"

    def append(self, item: T) -> None:
        self._items.append(item)

    def extend(self, items: Iterable[T]) -> None:
        self._items.extend(items)

    def insert(self, index: int, item: T) -> None:
        self._items.insert(index, item)

    def remove(self, item: T) -> None:
        self._items.remove(item)

    def pop(self, index: int = -1) -> T:
        return self._items.pop(index)

    def clear(self) -> None:
        self._items.clear()

    def to_list(self) -> list[T]:
        """Возвращает копию внутреннего списка."""
        return list(self._items)
