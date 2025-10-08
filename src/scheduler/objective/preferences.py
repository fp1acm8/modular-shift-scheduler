"""Preference-based objective terms."""
from __future__ import annotations

from typing import Iterable

from scheduler.data_models import PreferenceLevel, SchedulingInputs
from scheduler.objective.base import ObjectiveTerm
from scheduler.time_index import TimeSlot


class PreferenceSatisfaction(ObjectiveTerm):
    """Reward assignments that align with employee preferences."""

    def __init__(self, weight: float) -> None:
        super().__init__(name="preference_satisfaction", weight=weight)

    def apply(self, backend, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:  # type: ignore[override]
        terms = []
        for block in inputs.availability:
            if block.preference == PreferenceLevel.preferred:
                for slot in slots:
                    if block.start <= slot.start and slot.end <= block.end:
                        var = backend.get_variable(block.employee_id, slot.index)
                        terms.append((var, 1.0))
            elif block.preference == PreferenceLevel.unavailable:
                for slot in slots:
                    if block.start <= slot.start and slot.end <= block.end:
                        var = backend.get_variable(block.employee_id, slot.index)
                        terms.append((var, -2.0))
        if terms:
            backend.add_weighted_sum(terms, self.weight, name=self.name)


class WeekendDistribution(ObjectiveTerm):
    """Encourage fair distribution of weekend shifts."""

    def __init__(self, weight: float) -> None:
        super().__init__(name="weekend_distribution", weight=weight)

    def apply(self, backend, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:  # type: ignore[override]
        weekend_slots = [slot for slot in slots if slot.start.weekday() >= 5]
        if not weekend_slots:
            return
        for employee in inputs.employees:
            terms = [(backend.get_variable(employee.id, slot.index), 1.0) for slot in weekend_slots]
            backend.add_weighted_sum(terms, self.weight, name=f"weekend_{employee.id}")


class OvertimePenalty(ObjectiveTerm):
    """Penalise working beyond contracted hours."""

    def __init__(self, weight: float, overtime_threshold: float = 40.0) -> None:
        super().__init__(name="overtime_penalty", weight=weight)
        self.overtime_threshold = overtime_threshold

    def apply(self, backend, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:  # type: ignore[override]
        slots_list = list(slots)
        for employee in inputs.employees:
            terms = []
            for slot in slots_list:
                var = backend.get_variable(employee.id, slot.index)
                terms.append((var, slot.duration_hours))
            backend.add_weighted_sum(terms, self.weight / max(self.overtime_threshold, 1.0), name=f"overtime_{employee.id}")


__all__ = ["PreferenceSatisfaction", "WeekendDistribution", "OvertimePenalty"]
