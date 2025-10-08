"""Excel ingestion logic for scheduler inputs."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd
from pydantic import ValidationError

from scheduler.data_models import AvailabilityBlock, Employee, PreferenceLevel, SchedulingInputs, ShiftDemand


class ExcelStructureError(RuntimeError):
    """Raised when the workbook does not match expectations."""


class ExcelDataLoader:
    """Load scheduler inputs from a structured Excel workbook."""

    required_sheets = {"employees", "availability", "demand"}

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def validate_structure(self, workbook: Dict[str, pd.DataFrame]) -> None:
        missing = self.required_sheets - set(workbook)
        if missing:
            raise ExcelStructureError(f"Workbook missing sheets: {', '.join(sorted(missing))}")

    @staticmethod
    def _parse_datetime(value: object) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError(f"Cannot parse datetime from {value!r}")

    def load(self) -> SchedulingInputs:
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        workbook = pd.read_excel(self.path, sheet_name=None)
        self.validate_structure(workbook)

        employees = [self._parse_employee(row) for _, row in workbook["employees"].iterrows()]
        availability = [self._parse_availability(row) for _, row in workbook["availability"].iterrows()]
        demand = [self._parse_demand(row) for _, row in workbook["demand"].iterrows()]

        inputs = SchedulingInputs(employees=employees, availability=availability, demand=demand)
        self._validate_inputs(inputs)
        return inputs

    def _parse_employee(self, row: pd.Series) -> Employee:
        skills_raw = row.get("skills")
        skills: List[str] = []
        if isinstance(skills_raw, str):
            skills = [skill.strip() for skill in skills_raw.split(",") if skill.strip()]

        return Employee(
            id=str(row["id"]),
            name=str(row.get("name", row["id"])),
            max_hours_per_week=float(row.get("max_hours_per_week", 40)),
            skills=skills,
        )

    def _parse_availability(self, row: pd.Series) -> AvailabilityBlock:
        preference = PreferenceLevel(row.get("preference", PreferenceLevel.neutral))
        return AvailabilityBlock(
            employee_id=str(row["employee_id"]),
            start=self._parse_datetime(row["start"]),
            end=self._parse_datetime(row["end"]),
            preference=preference,
        )

    def _parse_demand(self, row: pd.Series) -> ShiftDemand:
        return ShiftDemand(
            start=self._parse_datetime(row["start"]),
            end=self._parse_datetime(row["end"]),
            required_staff=int(row.get("required_staff", 1)),
            skill=row.get("skill"),
        )

    def _validate_inputs(self, inputs: SchedulingInputs) -> None:
        employees = inputs.employees_by_id()
        for block in inputs.availability:
            if block.employee_id not in employees:
                raise ValidationError(
                    [
                        {
                            "loc": ("availability", block.employee_id),
                            "msg": "Unknown employee in availability",
                            "type": "value_error",
                        }
                    ],
                    AvailabilityBlock,
                )

        demand_span = sorted((demand.start, demand.end) for demand in inputs.demand)
        if demand_span and demand_span[0][0] >= demand_span[-1][1]:
            raise ValidationError(
                [
                    {
                        "loc": ("demand", 0),
                        "msg": "Demand window invalid",
                        "type": "value_error",
                    }
                ],
                ShiftDemand,
            )


__all__ = ["ExcelDataLoader", "ExcelStructureError"]
