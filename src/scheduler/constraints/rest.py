"""Rest period constraints."""
from __future__ import annotations

from typing import Iterable

from scheduler.constraints.base import BackendProtocol, Constraint
from scheduler.data_models import SchedulingInputs
from scheduler.time_index import TimeSlot


class RestPeriodConstraint(Constraint):
    """Require a minimum number of slots between assignments."""

    def __init__(self, min_rest_slots: int = 1) -> None:
        super().__init__(name="rest_period")
        self.min_rest_slots = min_rest_slots

    def apply(self, backend: BackendProtocol, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:
        slots_list = list(slots)
        for employee in inputs.employees:
            for i, slot in enumerate(slots_list):
                for j in range(1, self.min_rest_slots + 1):
                    if i + j < len(slots_list):
                        other_slot = slots_list[i + j]
                        backend.add_constraint(
                            [backend.get_variable(employee.id, slot.index), backend.get_variable(employee.id, other_slot.index)],
                            "<=",
                            1,
                            name=f"rest_{employee.id}_{slot.index}_{other_slot.index}",
                        )


__all__ = ["RestPeriodConstraint"]
