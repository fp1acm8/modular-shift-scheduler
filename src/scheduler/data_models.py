"""Domain data models used by the scheduler."""
from __future__ import annotations

from datetime import datetime, time
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, PositiveInt, validator


class PreferenceLevel(str, Enum):
    """Availability preference levels."""

    unavailable = "unavailable"
    neutral = "neutral"
    preferred = "preferred"


class Employee(BaseModel):
    """Employee metadata."""

    id: str
    name: str
    max_hours_per_week: float = Field(..., ge=0)
    skills: List[str] = Field(default_factory=list)


class AvailabilityBlock(BaseModel):
    """Employee availability over a time window."""

    employee_id: str
    start: datetime
    end: datetime
    preference: PreferenceLevel = PreferenceLevel.neutral

    @validator("end")
    def validate_order(cls, value: datetime, values: Dict[str, object]):  # noqa: D417
        start = values.get("start")
        if isinstance(start, datetime) and value <= start:
            raise ValueError("Availability end must be after start")
        return value


class ShiftDemand(BaseModel):
    """Demand for staff during a time window."""

    start: datetime
    end: datetime
    required_staff: PositiveInt
    skill: Optional[str] = None

    @validator("end")
    def validate_shift(cls, value: datetime, values: Dict[str, object]):  # noqa: D417
        start = values.get("start")
        if isinstance(start, datetime) and value <= start:
            raise ValueError("Demand end must be after start")
        return value


class SchedulingInputs(BaseModel):
    """Aggregated inputs loaded from data sources."""

    employees: List[Employee]
    availability: List[AvailabilityBlock]
    demand: List[ShiftDemand]

    def employees_by_id(self) -> Dict[str, Employee]:
        return {employee.id: employee for employee in self.employees}


class AssignmentDecision(BaseModel):
    """Single assignment decision."""

    employee_id: str
    slot_index: int
    start: datetime
    end: datetime
    is_assigned: bool


class SolverStatus(str, Enum):
    """Status of the solver run."""

    optimal = "optimal"
    feasible = "feasible"
    infeasible = "infeasible"
    unknown = "unknown"


class ScheduleSolution(BaseModel):
    """Solver results and metadata."""

    status: SolverStatus
    objective_value: Optional[float]
    assignments: List[AssignmentDecision]
    statistics: Dict[str, float] = Field(default_factory=dict)


__all__ = [
    "AssignmentDecision",
    "AvailabilityBlock",
    "Employee",
    "PreferenceLevel",
    "ScheduleSolution",
    "SchedulingInputs",
    "ShiftDemand",
    "SolverStatus",
]
