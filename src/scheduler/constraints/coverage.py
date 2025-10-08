"""Coverage constraints."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from scheduler.constraints.base import BackendProtocol, Constraint
from scheduler.data_models import SchedulingInputs
from scheduler.time_index import TimeSlot


class CoverageConstraint(Constraint):
    """Ensure each slot meets required staffing levels."""

    def __init__(self) -> None:
        super().__init__(name="coverage")

    def apply(self, backend: BackendProtocol, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:
        slot_to_demand = defaultdict(int)
        slot_list = list(slots)
        for demand in inputs.demand:
            for slot in slot_list:
                if slot.start < demand.end and demand.start < slot.end:
                    slot_to_demand[slot.index] = max(slot_to_demand[slot.index], demand.required_staff)

        for slot in slot_list:
            demand = slot_to_demand.get(slot.index)
            if not demand:
                continue
            expr = []
            for employee in inputs.employees:
                expr.append(backend.get_variable(employee.id, slot.index))
            backend.add_constraint(expr, ">=", demand, name=f"coverage_{slot.index}")


__all__ = ["CoverageConstraint"]
