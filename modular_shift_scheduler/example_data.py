"""Shared example configuration helpers used by tests and documentation."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import Employee, SchedulingConfig, ShiftDemand
from .xlsx_writer import write_workbook


def minimal_config() -> SchedulingConfig:
    """Return a validated configuration used across tests and examples."""

    employees = [
        Employee(
            identifier="alice",
            name="Alice",
            skills={"front", "back"},
            max_hours_per_week=20,
            cost_per_hour=15.0,
        ),
        Employee(
            identifier="bob",
            name="Bob",
            skills={"front"},
            max_hours_per_week=15,
            cost_per_hour=12.0,
        ),
    ]
    shifts = [
        ShiftDemand(
            identifier="shift_1",
            start=datetime(2024, 1, 1, 9),
            end=datetime(2024, 1, 1, 13),
            required_skill="front",
            required_employees=1,
            weight=1.0,
        ),
        ShiftDemand(
            identifier="shift_2",
            start=datetime(2024, 1, 1, 13),
            end=datetime(2024, 1, 1, 17),
            required_skill="back",
            required_employees=1,
            weight=2.0,
        ),
    ]

    config = SchedulingConfig(employees=employees, shifts=shifts, slot_minutes=60)
    config.validate()
    return config


def config_to_rows(config: SchedulingConfig) -> tuple[list[list[object]], list[list[object]]]:
    """Convert a configuration into row data for Excel sheets."""

    employees_rows = [
        ["id", "name", "skills", "max_hours_per_week", "cost_per_hour"],
        *[
            [
                employee.identifier,
                employee.name,
                ", ".join(sorted(employee.skills)),
                employee.max_hours_per_week,
                employee.cost_per_hour,
            ]
            for employee in config.employees
        ],
    ]
    shifts_rows = [
        ["id", "start", "end", "required_skill", "required_employees", "weight"],
        *[
            [
                shift.identifier,
                shift.start.isoformat(),
                shift.end.isoformat(),
                shift.required_skill,
                shift.required_employees,
                shift.weight,
            ]
            for shift in config.shifts
        ],
    ]
    return employees_rows, shifts_rows


def write_minimal_workbook(path: Path, config: SchedulingConfig | None = None) -> SchedulingConfig:
    """Write the minimal example workbook to ``path`` and return the config used."""

    config_to_write = minimal_config() if config is None else config
    employees_rows, shifts_rows = config_to_rows(config_to_write)
    write_workbook(path, employees_rows=employees_rows, shifts_rows=shifts_rows)
    return config_to_write


__all__ = ["minimal_config", "config_to_rows", "write_minimal_workbook"]
