"""Reporting helpers for solver results."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable

from rich.console import Console
from rich.table import Table

from scheduler.config import AppConfig
from scheduler.data_models import ScheduleSolution, SchedulingInputs
from scheduler.time_index import TimeSlot


def _slot_demand_map(inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> Dict[int, int]:
    demand_map: Dict[int, int] = defaultdict(int)
    slot_list = list(slots)
    for demand in inputs.demand:
        for slot in slot_list:
            if slot.start < demand.end and demand.start < slot.end:
                demand_map[slot.index] = max(demand_map[slot.index], demand.required_staff)
    return demand_map


def generate_kpis(inputs: SchedulingInputs, slots: Iterable[TimeSlot], solution: ScheduleSolution) -> Dict[str, float]:
    slot_list = list(slots)
    demand_map = _slot_demand_map(inputs, slot_list)
    slot_index_map = {slot.index: slot for slot in slot_list}
    coverage_met = 0
    coverage_slots = 0
    total_assignments = 0
    sunday_assignments = 0
    weekend_assignments = 0
    total_hours = 0.0

    assigned_by_slot: Dict[int, int] = defaultdict(int)
    for decision in solution.assignments:
        if not decision.is_assigned:
            continue
        assigned_by_slot[decision.slot_index] += 1
        total_assignments += 1
        slot = slot_index_map.get(decision.slot_index)
        if slot is None:
            continue
        total_hours += (slot.end - slot.start).total_seconds() / 3600
        if slot.start.weekday() == 6:
            sunday_assignments += 1
        if slot.start.weekday() >= 5:
            weekend_assignments += 1

    for slot in slot_list:
        required = demand_map.get(slot.index)
        if required is None or required <= 0:
            continue
        coverage_slots += 1
        if assigned_by_slot.get(slot.index, 0) >= required:
            coverage_met += 1

    coverage_ratio = coverage_met / coverage_slots if coverage_slots else 1.0

    return {
        "coverage_slots": float(coverage_slots),
        "coverage_met_ratio": coverage_ratio,
        "total_assignments": float(total_assignments),
        "total_assigned_hours": total_hours,
        "weekend_assignments": float(weekend_assignments),
        "sunday_assignments": float(sunday_assignments),
    }


def render_solution_table(solution: ScheduleSolution) -> Table:
    table = Table(title=f"Schedule Solution ({solution.status.value})", show_lines=False)
    table.add_column("Employee")
    table.add_column("Slot")
    table.add_column("Start")
    table.add_column("End")
    for decision in solution.assignments:
        if decision.is_assigned:
            table.add_row(decision.employee_id, str(decision.slot_index), str(decision.start), str(decision.end))
    return table


def explain_configuration(config: AppConfig) -> str:
    lines = ["Configuration Summary:"]
    lines.append(f"  Horizon: {config.time.start_date} -> {config.time.end_date} ({config.time.slot_minutes}m slots)")
    lines.append(f"  Workbook: {config.files.workbook_path}")
    if config.files.output_path:
        lines.append(f"  Output: {config.files.output_path}")
    lines.append("  Constraints:")
    for field, value in config.toggles.model_dump().items():
        lines.append(f"    - {field.replace('_', ' ').title()}: {'ON' if value else 'off'}")
    lines.append("  Objective Weights:")
    for field, value in config.objective.model_dump().items():
        lines.append(f"    - {field.replace('_', ' ').title()}: {value}")
    return "\n".join(lines)


def print_report(solution: ScheduleSolution) -> None:
    console = Console()
    table = render_solution_table(solution)
    console.print(table)
    if solution.statistics:
        stats_table = Table(title="KPIs")
        stats_table.add_column("Metric")
        stats_table.add_column("Value")
        for key, value in solution.statistics.items():
            stats_table.add_row(key, f"{value:.2f}" if isinstance(value, float) else str(value))
        console.print(stats_table)


__all__ = ["explain_configuration", "generate_kpis", "print_report", "render_solution_table"]
