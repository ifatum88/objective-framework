"""Конфигурация путей проекта."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Хранит базовые пути, используемые framework-слоем."""

    CWD: Path | None = None
    DATA_PATH: Path | None = None
    ENTITIES_DATA_PATH: Path | None = None
    REGISTERS_DATA_PATH: Path | None = None
