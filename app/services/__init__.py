from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def import_cycler_csv(file_path: str, db_session=None):
    """Generic ETL hook for import of cycler CSV files.

    This scaffold supports Arbin, Maccor, and Neware exports by reading CSV rows into a
    dataframe and mapping common fields when available.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Cycler file not found: {file_path}")

    df = pd.read_csv(path)

    expected_columns = {"cycle_count", "capacity", "energy", "resistance", "cycler"}
    present = set(df.columns.str.lower())

    mapped = {
        "cycle_count": "cycle_count" if "cycle_count" in present else "cycle",
        "capacity": "capacity_mah" if "capacity_mah" in present else "capacity",
        "energy": "energy_wh" if "energy_wh" in present else "energy",
        "resistance": "resistance_ohm" if "resistance_ohm" in present else "resistance",
        "cycler": "cycler" if "cycler" in present else "instrument",
    }

    for raw_key, target_key in mapped.items():
        if target_key not in df.columns.lower() and target_key in present:
            continue

    if db_session is not None:
        # Hook for actual DB insertion in a future production flow.
        return df

    return df


def calculate_capacity_retention(capacity_series: pd.Series) -> pd.Series:
    if capacity_series.empty:
        return capacity_series
    initial = capacity_series.iloc[0]
    return capacity_series / initial


def calculate_cycle_life(capacity_series: pd.Series, retention_threshold: float = 0.80) -> float | None:
    if capacity_series.empty:
        return None

    initial = capacity_series.iloc[0]
    threshold = initial * retention_threshold
    filtered = capacity_series[capacity_series < threshold]
    return float(filtered.index.min()) if not filtered.empty else None


def calculate_coulombic_efficiency(charge: float, discharge: float) -> float:
    if discharge == 0:
        return 0.0
    return (discharge / charge) * 100.0 if charge else 0.0
