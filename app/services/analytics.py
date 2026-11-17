"""Battery performance calculations with explicit empty/invalid input handling."""

import pandas as pd


def calculate_capacity_retention(capacity_series: pd.Series) -> pd.Series:
    values = pd.to_numeric(capacity_series, errors="coerce")
    valid = values.dropna()
    if valid.empty or valid.iloc[0] == 0:
        return pd.Series(index=values.index, dtype="float64", name="capacity_retention")
    return (values / valid.iloc[0]).rename("capacity_retention")


def calculate_cycle_life(capacity_series: pd.Series, retention_threshold: float = 0.80) -> int | None:
    if not 0 < retention_threshold <= 1:
        raise ValueError("retention_threshold must be in (0, 1]")
    values = pd.to_numeric(capacity_series, errors="coerce").dropna()
    if values.empty or values.iloc[0] <= 0:
        return None
    below = values[values < values.iloc[0] * retention_threshold]
    return int(below.index[0]) if not below.empty else None


def calculate_coulombic_efficiency(charge: float, discharge: float) -> float | None:
    if charge <= 0 or discharge < 0:
        return None
    return (discharge / charge) * 100.0
