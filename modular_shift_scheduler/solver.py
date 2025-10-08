"""High level solver orchestration for the modular shift scheduler."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple

from .config import SchedulingConfig
from .constraints import (
    AssignmentsByEmployee,
    assignment_candidates,
)
from .objectives import total_objective
from .time_index import TimeIndexer


@dataclass(slots=True)
class SolveResult:
    status: str
    objective_value: float
    assignments: Dict[str, List[str]]
    shortage_by_shift: Dict[str, int]

    def assigned_pairs(self) -> List[Tuple[str, str]]:
        return [
            (employee, shift)
            for employee, shifts in self.assignments.items()
            for shift in shifts
        ]


class SolverError(RuntimeError):
    """Raised when the search fails to find a feasible solution."""


def solve(config: SchedulingConfig) -> SolveResult:
    config.validate()
    indexer = TimeIndexer.from_shifts(config.shifts, slot_minutes=config.slot_minutes)
    candidates = assignment_candidates(config)
    employees = {employee.identifier: employee for employee in config.employees}
    shifts = sorted(config.shifts, key=lambda shift: (shift.start, shift.identifier))

    assignments_by_employee: AssignmentsByEmployee = {
        employee.identifier: [] for employee in config.employees
    }
    shortages: Dict[str, int] = {shift.identifier: 0 for shift in config.shifts}

    best_assignments: Dict[str, List[str]] | None = None
    best_shortages: Dict[str, int] | None = None
    best_objective = float("inf")

    def is_feasible(employee_id: str, shift_index: int) -> bool:
        shift = shifts[shift_index]
        # Check overlap
        for other_shift_id in assignments_by_employee[employee_id]:
            other_shift = shift_lookup[other_shift_id]
            if shift.start < other_shift.end and other_shift.start < shift.end:
                return False
        # Check max hours
        duration = indexer.duration_for_shift(shift)
        current_hours = sum(
            indexer.duration_for_shift(shift_lookup[assigned_shift])
            for assigned_shift in assignments_by_employee[employee_id]
        )
        return current_hours + duration <= employees[employee_id].max_hours_per_week + 1e-6

    shift_lookup = {shift.identifier: shift for shift in config.shifts}

    def search(shift_index: int) -> None:
        nonlocal best_assignments, best_objective, best_shortages
        if shift_index == len(shifts):
            objective = total_objective(assignments_by_employee, shortages, config, indexer)
            if objective < best_objective:
                best_objective = objective
                best_assignments = {
                    employee_id: list(shift_ids)
                    for employee_id, shift_ids in assignments_by_employee.items()
                }
                best_shortages = dict(shortages)
            return

        shift = shifts[shift_index]
        eligible_employees = candidates[shift.identifier]
        max_assignable = min(len(eligible_employees), shift.required_employees)
        # Explore in descending order of assigned employees to find feasible solutions quickly.
        for count in range(max_assignable, -1, -1):
            for combo in combinations(eligible_employees, count):
                if not all(is_feasible(employee_id, shift_index) for employee_id in combo):
                    continue
                for employee_id in combo:
                    assignments_by_employee[employee_id].append(shift.identifier)
                shortages[shift.identifier] = shift.required_employees - count

                partial_objective = total_objective(assignments_by_employee, shortages, config, indexer)
                if partial_objective < best_objective:
                    search(shift_index + 1)

                for employee_id in combo:
                    assignments_by_employee[employee_id].pop()
                shortages[shift.identifier] = 0

    search(0)

    if best_assignments is None or best_shortages is None:
        raise SolverError("No feasible assignment found")

    return SolveResult(
        status="Optimal",
        objective_value=best_objective,
        assignments=best_assignments,
        shortage_by_shift=best_shortages,
    )
