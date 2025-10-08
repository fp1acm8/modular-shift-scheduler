from __future__ import annotations

import pytest

from modular_shift_scheduler.objectives import labour_cost, shortage_penalty, total_objective
from modular_shift_scheduler.time_index import TimeIndexer


def test_labour_cost_uses_employee_rates(basic_config):
    indexer = TimeIndexer.from_shifts(basic_config.shifts, basic_config.slot_minutes)
    assignments = {"alice": ["shift_1", "shift_2"], "bob": ["shift_1"]}
    cost = labour_cost(assignments, basic_config, indexer)
    expected = 15 * 8 + 12 * 4
    assert cost == pytest.approx(expected)


def test_shortage_penalty_scales_with_weight(basic_config):
    shortages = {"shift_1": 0, "shift_2": 1}
    penalty = shortage_penalty(shortages, basic_config)
    expected = basic_config.shortage_penalty_per_employee * basic_config.shifts[1].weight
    assert penalty == pytest.approx(expected)


def test_total_objective_combines_terms(basic_config):
    indexer = TimeIndexer.from_shifts(basic_config.shifts, basic_config.slot_minutes)
    assignments = {"alice": ["shift_1"], "bob": []}
    shortages = {"shift_1": 0, "shift_2": 1}
    total = total_objective(assignments, shortages, basic_config, indexer)
    expected = labour_cost(assignments, basic_config, indexer) + shortage_penalty(
        shortages, basic_config
    )
    assert total == pytest.approx(expected)
