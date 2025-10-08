"""Constraint helpers used by the search based solver."""
from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Tuple

from .config import Employee, SchedulingConfig, ShiftDemand
from .time_index import TimeIndexer

AssignmentsByEmployee = Dict[str, List[str]]
def assignment_candidates(config: SchedulingConfig) -> Dict[str, List[str]]:
    candidates: Dict[str, List[str]] = {}
    for shift in config.shifts:
        candidates[shift.identifier] = [
            employee.identifier
            for employee in config.employees
            if shift.required_skill in employee.skills
        ]
    return candidates


def shortage_for_shift(shift: ShiftDemand, assigned_employees: Iterable[str]) -> int:
    assigned_count = len(list(assigned_employees))
    return max(0, shift.required_employees - assigned_count)


def hours_used_by_employee(
    assignments: AssignmentsByEmployee,
    config: SchedulingConfig,
    indexer: TimeIndexer,
) -> Dict[str, float]:
    shift_lookup = {shift.identifier: shift for shift in config.shifts}
    hours: Dict[str, float] = {employee.identifier: 0.0 for employee in config.employees}
    for employee_id, shift_ids in assignments.items():
        total = 0.0
        for shift_id in shift_ids:
            shift = shift_lookup[shift_id]
            total += indexer.duration_for_shift(shift)
        hours[employee_id] = total
    return hours


def max_hours_respected(
    assignments: AssignmentsByEmployee,
    config: SchedulingConfig,
    indexer: TimeIndexer,
) -> bool:
    hours = hours_used_by_employee(assignments, config, indexer)
    for employee in config.employees:
        if hours[employee.identifier] - 1e-6 > employee.max_hours_per_week:
            return False
    return True


def overlapping_shifts_for_employee(
    employee_id: str,
    assignments: AssignmentsByEmployee,
    shift_lookup: Mapping[str, ShiftDemand],
) -> List[Tuple[str, str]]:
    overlaps: List[Tuple[str, str]] = []
    shift_ids = assignments.get(employee_id, [])
    for i, shift_id in enumerate(shift_ids):
        for other_shift_id in shift_ids[i + 1 :]:
            shift_a = shift_lookup[shift_id]
            shift_b = shift_lookup[other_shift_id]
            if shift_a.start < shift_b.end and shift_b.start < shift_a.end:
                overlaps.append((shift_id, other_shift_id))
    return overlaps


def no_overlaps(assignments: AssignmentsByEmployee, config: SchedulingConfig) -> bool:
    shift_lookup = {shift.identifier: shift for shift in config.shifts}
    for employee in config.employees:
        if overlapping_shifts_for_employee(employee.identifier, assignments, shift_lookup):
            return False
    return True
