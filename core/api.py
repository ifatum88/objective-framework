"""Публичная точка входа framework-а."""

from pathlib import Path

import pandas as pd

from .base import Config
from .meta import Entity, LookupConfig, OptionalData
from .store import Catalog, Registry

config = Config()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

config.CWD = PROJECT_ROOT
config.DATA_PATH = PROJECT_ROOT / "_prod_data"
config.ENTITIES_DATA_PATH = config.DATA_PATH / "entities"
config.REGISTERS_DATA_PATH = config.DATA_PATH / "registers"

__all__ = [
    "pd",
    "Entity",
    "LookupConfig",
    "OptionalData",
    "Catalog",
    "Registry",
    "Config",
    "Path",
    "config",
]
