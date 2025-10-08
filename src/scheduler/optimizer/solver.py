"""Solver orchestration for the scheduling engine."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from ortools.sat.python import cp_model

from scheduler import reporting
from scheduler.config import AppConfig, resolve_paths
from scheduler.constraints import CoverageConstraint, DailyLimitConstraint, MaxHoursConstraint, RestPeriodConstraint
from scheduler.data_models import AssignmentDecision, ScheduleSolution, SchedulingInputs, SolverStatus
from scheduler.io.excel_loader import ExcelDataLoader
from scheduler.objective import OvertimePenalty, PreferenceSatisfaction, WeekendDistribution
from scheduler.optimizer.backend import CPSatBackend
from scheduler.time_index import TimeIndexer, TimeSlot


class SolverOrchestrator:
    """High level API to run the scheduler."""

    def __init__(self, config: AppConfig, base_dir: Path | None = None) -> None:
        self.config = resolve_paths(config, base_dir)

    def load_inputs(self) -> SchedulingInputs:
        loader = ExcelDataLoader(self.config.files.workbook_path)
        return loader.load()

    def build_time_slots(self, inputs: SchedulingInputs) -> List[TimeSlot]:  # noqa: ARG002
        start = datetime.fromisoformat(self.config.time.start_date)
        end = datetime.fromisoformat(self.config.time.end_date)
        indexer = TimeIndexer(start=start, end=end, slot_minutes=self.config.time.slot_minutes)
        return indexer.build()

    def register_constraints(self, backend: CPSatBackend, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> List[str]:
        applied: List[str] = []
        toggles = self.config.toggles
        if toggles.enforce_coverage:
            CoverageConstraint().apply(backend, inputs, slots)
            applied.append("coverage")
        if toggles.enforce_max_hours:
            MaxHoursConstraint().apply(backend, inputs, slots)
            applied.append("max_hours")
        if toggles.enforce_daily_limits:
            DailyLimitConstraint().apply(backend, inputs, slots)
            applied.append("daily_limit")
        if toggles.enforce_rest_periods:
            RestPeriodConstraint(min_rest_slots=1).apply(backend, inputs, slots)
            applied.append("rest_period")
        return applied

    def register_objective(self, backend: CPSatBackend, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> List[str]:
        weights = self.config.objective
        applied: List[str] = []
        if weights.honor_preferences:
            PreferenceSatisfaction(weights.honor_preferences).apply(backend, inputs, slots)
            applied.append("preferences")
        if weights.distribute_weekends and self.config.toggles.balance_weekend_shifts:
            WeekendDistribution(weights.distribute_weekends).apply(backend, inputs, slots)
            applied.append("weekend_distribution")
        if weights.minimize_overtime:
            OvertimePenalty(weights.minimize_overtime).apply(backend, inputs, slots)
            applied.append("overtime")
        return applied

    def solve(self) -> ScheduleSolution:
        inputs = self.load_inputs()
        slots = self.build_time_slots(inputs)
        backend = CPSatBackend(inputs, slots)
        self.register_constraints(backend, inputs, slots)
        self.register_objective(backend, inputs, slots)

        solver_result = backend.solve(
            time_limit_seconds=self.config.solver.time_limit_seconds,
            num_workers=self.config.solver.num_workers,
            log_search=self.config.solver.log_search_progress,
        )
        solution = self._build_solution(inputs, slots, backend, solver_result)
        solution.statistics.update(reporting.generate_kpis(inputs, slots, solution))
        return solution

    def _build_solution(
        self,
        inputs: SchedulingInputs,
        slots: Iterable[TimeSlot],
        backend: CPSatBackend,
        solver_result,
    ) -> ScheduleSolution:
        status = self._translate_status(solver_result.status)
        assignments: List[AssignmentDecision] = []
        solver = solver_result.solver
        for employee in inputs.employees:
            for slot in slots:
                var = backend.get_variable(employee.id, slot.index)
                assignments.append(
                    AssignmentDecision(
                        employee_id=employee.id,
                        slot_index=slot.index,
                        start=slot.start,
                        end=slot.end,
                        is_assigned=bool(solver.Value(var)),
                    )
                )
        objective_value = solver.ObjectiveValue() if backend.has_objective() else None
        return ScheduleSolution(status=status, objective_value=objective_value, assignments=assignments)

    @staticmethod
    def _translate_status(status: int) -> SolverStatus:
        mapping = {
            cp_model.OPTIMAL: SolverStatus.optimal,
            cp_model.FEASIBLE: SolverStatus.feasible,
            cp_model.INFEASIBLE: SolverStatus.infeasible,
            cp_model.UNKNOWN: SolverStatus.unknown,
        }
        return mapping.get(status, SolverStatus.unknown)


__all__ = ["SolverOrchestrator"]
