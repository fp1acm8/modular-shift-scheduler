"""Objective calculations for the search based solver."""
from __future__ import annotations

from typing import Mapping

from .config import SchedulingConfig
from .constraints import AssignmentsByEmployee
from .time_index import TimeIndexer


def labour_cost(
    assignments: AssignmentsByEmployee,
    config: SchedulingConfig,
    indexer: TimeIndexer,
) -> float:
    shift_lookup = {shift.identifier: shift for shift in config.shifts}
    total = 0.0
    for employee in config.employees:
        for shift_id in assignments.get(employee.identifier, []):
            shift = shift_lookup[shift_id]
            hours = indexer.duration_for_shift(shift)
            total += employee.cost_per_hour * hours
    return total


def shortage_penalty(
    shortages: Mapping[str, int], config: SchedulingConfig
) -> float:
    shift_lookup = {shift.identifier: shift for shift in config.shifts}
    penalty = 0.0
    for shift_id, shortage in shortages.items():
        if shortage <= 0:
            continue
        penalty += shortage * config.shortage_penalty_per_employee * shift_lookup[shift_id].weight
    return penalty


def total_objective(
    assignments: AssignmentsByEmployee,
    shortages: Mapping[str, int],
    config: SchedulingConfig,
    indexer: TimeIndexer,
) -> float:
    return labour_cost(assignments, config, indexer) + shortage_penalty(shortages, config)
