"""CP-SAT backend abstractions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from ortools.sat.python import cp_model

from scheduler.data_models import SchedulingInputs
from scheduler.time_index import TimeSlot


@dataclass
class SolverResult:
    status: int
    solver: cp_model.CpSolver


class CPSatBackend:
    """Thin wrapper around OR-Tools CP-SAT for workforce scheduling."""

    def __init__(self, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:
        self.inputs = inputs
        self.slots = list(slots)
        self.model = cp_model.CpModel()
        self._variables: Dict[Tuple[str, int], cp_model.IntVar] = {}
        self._objective_terms: List[Tuple[cp_model.LinearExpr, float]] = []
        self._build_variables()

    def _build_variables(self) -> None:
        for employee in self.inputs.employees:
            for slot in self.slots:
                var = self.model.NewBoolVar(f"assign_{employee.id}_{slot.index}")
                self._variables[(employee.id, slot.index)] = var

    def get_variable(self, employee_id: str, slot_index: int) -> cp_model.IntVar:
        return self._variables[(employee_id, slot_index)]

    def add_constraint(self, terms, operator: str, rhs: float, name: str | None = None) -> None:
        if not terms:
            return
        if isinstance(terms[0], tuple):
            expr = sum(coeff * var for var, coeff in terms)
        else:
            expr = sum(terms)
        if operator == "<=":
            ct = self.model.Add(expr <= rhs)
        elif operator == ">=":
            ct = self.model.Add(expr >= rhs)
        elif operator == "==":
            ct = self.model.Add(expr == rhs)
        else:
            raise ValueError(f"Unsupported operator: {operator}")
        if name:
            ct.WithName(name)

    def add_weighted_sum(self, terms, weight: float, name: str) -> None:
        if not terms or weight == 0:
            return
        expr = sum(coeff * var for var, coeff in terms)
        self._objective_terms.append((expr, weight))

    def has_objective(self) -> bool:
        return bool(self._objective_terms)

    def solve(self, time_limit_seconds: int | None = None, num_workers: int | None = None, log_search: bool = False) -> SolverResult:
        if self._objective_terms:
            objective = sum(weight * expr for expr, weight in self._objective_terms)
            self.model.Maximize(objective)

        solver = cp_model.CpSolver()
        if time_limit_seconds is not None:
            solver.parameters.max_time_in_seconds = time_limit_seconds
        if num_workers is not None:
            solver.parameters.num_search_workers = num_workers
        solver.parameters.log_search_progress = log_search

        status = solver.Solve(self.model)
        return SolverResult(status=status, solver=solver)


__all__ = ["CPSatBackend", "SolverResult"]
