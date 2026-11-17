import pandas as pd
import pytest

from app.services.analytics import calculate_capacity_retention, calculate_coulombic_efficiency, calculate_cycle_life


def test_capacity_retention_uses_first_valid_value():
    result = calculate_capacity_retention(pd.Series([None, 10.0, 8.0]))
    assert result.iloc[1] == 1.0
    assert result.iloc[2] == 0.8


def test_cycle_life_returns_first_index_below_threshold():
    assert calculate_cycle_life(pd.Series([100.0, 90.0, 79.0], index=[1, 2, 3])) == 3


def test_cycle_life_handles_no_crossing_and_empty():
    assert calculate_cycle_life(pd.Series(dtype=float)) is None
    assert calculate_cycle_life(pd.Series([100.0, 90.0])) is None


def test_coulombic_efficiency_invalid_charge():
    assert calculate_coulombic_efficiency(0, 5) is None
    assert calculate_coulombic_efficiency(10, 9.5) == 95.0


def test_cycler_csv_normalizes_and_rejects_bad_file(tmp_path):
    from app.services.cycler_import import import_cycler_csv
    path = tmp_path / "cycles.csv"
    path.write_text("Cycle,Charge Capacity,Discharge Capacity\n1,2.1,2.0\n", encoding="utf-8")
    frame = import_cycler_csv(path)
    assert list(frame["cycle_number"]) == [1]
    assert frame["discharge_capacity"].iloc[0] == 2.0
    with pytest.raises(FileNotFoundError):
        import_cycler_csv(tmp_path / "missing.csv")
