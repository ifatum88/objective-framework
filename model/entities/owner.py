from dataclasses import dataclass

from core.meta import Entity, LookupConfig

from .domain import Domain


@dataclass(frozen=True)
class Owner(Entity):
    """Сущность владельца, связанная со справочником доменов."""

    code: str
    name: str
    domain: Domain
    default: int = 0

    __lookup__ = LookupConfig(
        search_by="code",
        export_field="code"
    )
