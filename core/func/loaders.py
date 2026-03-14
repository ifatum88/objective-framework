"""Функции загрузки исходных данных."""

from pathlib import Path

from pandas import DataFrame, read_excel


def loader_from_excel(excel_path: Path, **excel_kwargs) -> DataFrame:
    """Читает Excel-файл и возвращает pandas.DataFrame."""
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    return read_excel(excel_path, engine="openpyxl", **excel_kwargs)
