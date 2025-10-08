"""Working hours constraints."""
from __future__ import annotations

from typing import Iterable

from scheduler.constraints.base import BackendProtocol, Constraint
from scheduler.data_models import SchedulingInputs
from scheduler.time_index import TimeSlot


class MaxHoursConstraint(Constraint):
    """Ensure employees do not exceed contracted hours."""

    def __init__(self) -> None:
        super().__init__(name="max_hours")

    def apply(self, backend: BackendProtocol, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:
        slots_list = list(slots)
        for employee in inputs.employees:
            expr = []
            for slot in slots_list:
                var = backend.get_variable(employee.id, slot.index)
                expr.append((var, slot.duration_hours))
            backend.add_constraint(expr, "<=", employee.max_hours_per_week, name=f"max_hours_{employee.id}")


class DailyLimitConstraint(Constraint):
    """Prevent employees from working more than one slot per day."""

    def __init__(self) -> None:
        super().__init__(name="daily_limit")

    def apply(self, backend: BackendProtocol, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:
        slots_by_day = {}
        for slot in slots:
            day = slot.start.date()
            slots_by_day.setdefault(day, []).append(slot)

        for employee in inputs.employees:
            for day, day_slots in slots_by_day.items():
                vars_ = [backend.get_variable(employee.id, slot.index) for slot in day_slots]
                backend.add_constraint(vars_, "<=", 1, name=f"daily_limit_{employee.id}_{day}")


__all__ = ["MaxHoursConstraint", "DailyLimitConstraint"]
