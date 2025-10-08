from __future__ import annotations

import pytest

from modular_shift_scheduler.time_index import TimeIndexer


def test_time_index_from_shifts(basic_config):
    indexer = TimeIndexer.from_shifts(basic_config.shifts, basic_config.slot_minutes)
    assert indexer.num_slots() == 8
    assert indexer.index(basic_config.shifts[0].start) == 0
    assert indexer.index(basic_config.shifts[1].start) == 4


def test_time_index_validation(basic_config):
    indexer = TimeIndexer.from_shifts(basic_config.shifts, basic_config.slot_minutes)
    with pytest.raises(ValueError):
        indexer.index(basic_config.shifts[0].start.replace(hour=10, minute=30))
