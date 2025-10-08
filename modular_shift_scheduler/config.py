"""Core configuration models for the modular shift scheduler."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, List, Sequence, Set


@dataclass(slots=True)
class Employee:
    """Represents a single worker that may be assigned to shifts."""

    identifier: str
    name: str
    skills: Set[str]
    max_hours_per_week: float
    cost_per_hour: float = 0.0

    def __post_init__(self) -> None:  # pragma: no cover - defensive programming
        self.identifier = str(self.identifier)
        self.name = str(self.name)
        self.skills = {skill.strip().lower() for skill in self.skills if skill.strip()}
        if self.max_hours_per_week < 0:
            raise ValueError("max_hours_per_week must be non-negative")
        if self.cost_per_hour < 0:
            raise ValueError("cost_per_hour must be non-negative")


@dataclass(slots=True)
class ShiftDemand:
    """Represents the demand for a single shift block."""

    identifier: str
    start: datetime
    end: datetime
    required_skill: str
    required_employees: int
    weight: float = 1.0

    def __post_init__(self) -> None:  # pragma: no cover - defensive programming
        if self.end <= self.start:
            raise ValueError("Shift end must be after start")
        if self.required_employees < 0:
            raise ValueError("required_employees must be non-negative")
        if self.weight <= 0:
            raise ValueError("weight must be positive")
        self.required_skill = self.required_skill.strip().lower()

    @property
    def duration(self) -> timedelta:
        return self.end - self.start


@dataclass(slots=True)
class SchedulingConfig:
    """Aggregates employees, shift demands and global solver options."""

    employees: List[Employee] = field(default_factory=list)
    shifts: List[ShiftDemand] = field(default_factory=list)
    slot_minutes: int = 60
    shortage_penalty_per_employee: float = 100.0

    def validate(self) -> None:
        if self.slot_minutes <= 0:
            raise ValueError("slot_minutes must be greater than zero")
        self._validate_unique_ids(self.employees, "employee")
        self._validate_unique_ids(self.shifts, "shift")
        if not self.employees:
            raise ValueError("At least one employee is required")
        if not self.shifts:
            raise ValueError("At least one shift is required")

    @staticmethod
    def _validate_unique_ids(items: Sequence[object], label: str) -> None:
        seen: Set[str] = set()
        for item in items:
            identifier = getattr(item, "identifier", None)
            if identifier in seen:
                raise ValueError(f"Duplicate {label} identifier: {identifier}")
            seen.add(identifier)

    def all_skills(self) -> Set[str]:
        skills: Set[str] = set()
        for employee in self.employees:
            skills.update(employee.skills)
        return skills

    def required_skills(self) -> Set[str]:
        return {shift.required_skill for shift in self.shifts}

    def employees_with_skill(self, skill: str) -> Iterable[Employee]:
        skill_lower = skill.strip().lower()
        return (emp for emp in self.employees if skill_lower in emp.skills)
