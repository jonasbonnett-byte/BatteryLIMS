"""Cycler CSV loader and normalized column mapping helpers."""

from pathlib import Path
import re

import pandas as pd

COLUMN_ALIASES = {
    "cycle_number": ("cycle", "cycle index", "cycle_index", "cycle number", "cycle_number"),
    "charge_capacity": ("charge capacity", "charge_capacity", "chg capacity", "charge_mah"),
    "discharge_capacity": ("discharge capacity", "discharge_capacity", "dchg capacity", "discharge_mah"),
    "coulombic_efficiency": ("coulombic efficiency", "coulombic_efficiency", "ce"),
    "energy_wh": ("energy", "energy_wh", "discharge energy"),
    "dc_resistance": ("dc resistance", "dc_resistance", "resistance", "resistance_ohm"),
    "timestamp_recorded": ("timestamp", "date/time", "datetime", "time", "timestamp_recorded"),
}


def _normalize_header(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def import_cycler_csv(file_path: str | Path, *, cycler_type: str | None = None) -> pd.DataFrame:
    """Read a CSV export and normalize recognized columns.

    Vendor exports vary by software version; this intentionally maps common headers
    only. Review the returned dataframe before persisting data in production.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Cycler file not found: {path}")
    raw = pd.read_csv(path)
    header_map = {_normalize_header(column): column for column in raw.columns}
    rename = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if _normalize_header(alias) in header_map:
                rename[header_map[_normalize_header(alias)]] = canonical
                break
    result = raw.rename(columns=rename).copy()
    if "cycle_number" in result:
        result["cycle_number"] = pd.to_numeric(result["cycle_number"], errors="coerce").astype("Int64")
    for column in set(COLUMN_ALIASES) - {"cycle_number", "timestamp_recorded"}:
        if column in result:
            result[column] = pd.to_numeric(result[column], errors="coerce")
    if "timestamp_recorded" in result:
        result["timestamp_recorded"] = pd.to_datetime(result["timestamp_recorded"], errors="coerce")
    result.attrs["source_file"] = str(path)
    result.attrs["cycler_type"] = cycler_type
    return result
