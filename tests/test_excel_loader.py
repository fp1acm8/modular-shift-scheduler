from __future__ import annotations

import pytest

from modular_shift_scheduler.excel_loader import load_config_from_excel
from modular_shift_scheduler.xlsx_writer import write_workbook


def test_load_config_from_excel_round_trip(excel_fixture_path):
    config = load_config_from_excel(excel_fixture_path)
    assert len(config.employees) == 2
    assert {emp.identifier for emp in config.employees} == {"alice", "bob"}
    assert {shift.identifier for shift in config.shifts} == {"shift_1", "shift_2"}


def test_missing_sheet_raises(tmp_path):
    broken = tmp_path / "broken.xlsx"
    write_workbook(
        broken,
        employees_rows=[["id", "name", "skills", "max_hours_per_week"], ["a", "A", "front", 10]],
        shifts_rows=None,
    )

    with pytest.raises(ValueError):
        load_config_from_excel(broken)
