from dataclasses import dataclass

from core.meta import Entity, LookupConfig


@dataclass(frozen=True)
class Asset(Entity):
    """Справочник активов."""

    code: str
    name: str
    default: int = 0

    __lookup__ = LookupConfig(
        search_by = "code",
        export_field = "code"
    )
