from dataclasses import dataclass

from core.meta import Entity, LookupConfig


@dataclass(frozen=True)
class Domain(Entity):
    """Справочник доменов/направлений."""

    code: str
    name: str
    default: int = 0

    __lookup__ = LookupConfig(
        search_by = "name",
        export_field = "code"
    )
