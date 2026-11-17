from __future__ import annotations

import pandas as pd


def import_cycler_csv(file_path: str):
    """Simple CSV loader for battery cycler exports."""
    df = pd.read_csv(file_path)
    return df


def calculate_capacity_retention(capacity_series: pd.Series) -> pd.Series:
    if capacity_series.empty:
        return capacity_series
    return capacity_series / capacity_series.iloc[0]


def calculate_cycle_life(capacity_series: pd.Series, retention_threshold: float = 0.80) -> float | None:
    if capacity_series.empty:
        return None
    initial = capacity_series.iloc[0]
    threshold_value = initial * retention_threshold
    filtered = capacity_series[capacity_series < threshold_value]
    return float(filtered.index.min()) if not filtered.empty else None


def calculate_coulombic_efficiency(charge: float, discharge: float) -> float:
    if discharge == 0:
        return 0.0
    return (discharge / charge) * 100 if charge else 0.0
