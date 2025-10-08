from __future__ import annotations

import copy

from modular_shift_scheduler.constraints import (
    assignment_candidates,
    hours_used_by_employee,
    max_hours_respected,
    no_overlaps,
    shortage_for_shift,
)
from modular_shift_scheduler.time_index import TimeIndexer


def test_assignment_candidates_filter_by_skill(basic_config):
    candidates = assignment_candidates(basic_config)
    assert candidates["shift_1"] == ["alice", "bob"]
    assert candidates["shift_2"] == ["alice"]


def test_shortage_for_shift_counts_missing_staff(basic_config):
    shift = basic_config.shifts[0]
    assert shortage_for_shift(shift, ["alice"]) == 0
    assert shortage_for_shift(shift, []) == 1


def test_hours_used_by_employee(basic_config):
    indexer = TimeIndexer.from_shifts(basic_config.shifts, basic_config.slot_minutes)
    assignments = {"alice": ["shift_1", "shift_2"], "bob": []}
    hours = hours_used_by_employee(assignments, basic_config, indexer)
    assert hours["alice"] == 8
    assert hours["bob"] == 0


def test_max_hours_and_overlap_constraints(basic_config):
    indexer = TimeIndexer.from_shifts(basic_config.shifts, basic_config.slot_minutes)
    assignments = {"alice": ["shift_1", "shift_2"], "bob": ["shift_1"]}
    assert max_hours_respected(assignments, basic_config, indexer)
    assert no_overlaps(assignments, basic_config)

    limited_config = copy.deepcopy(basic_config)
    limited_config.employees[0].max_hours_per_week = 4
    assert not max_hours_respected(assignments, limited_config, indexer)

    # Force overlap by creating overlapping shift times
    overlapping_config = copy.deepcopy(basic_config)
    overlapping_assignments = {"alice": ["shift_1", "shift_2"]}
    overlapping_config.shifts[1].start = overlapping_config.shifts[0].start
    overlapping_config.shifts[1].end = overlapping_config.shifts[0].end
    assert not no_overlaps(overlapping_assignments, overlapping_config)
