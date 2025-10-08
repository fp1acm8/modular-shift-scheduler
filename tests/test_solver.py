from __future__ import annotations

from modular_shift_scheduler.solver import solve


def test_solver_produces_feasible_schedule(basic_config):
    result = solve(basic_config)
    assert result.status == "Optimal"
    # Both shifts should be covered without shortage
    assert all(value == 0.0 for value in result.shortage_by_shift.values())
    # Each shift should be staffed by a worker with the appropriate skill
    assigned_pairs = set(result.assigned_pairs())
    assert ("alice", "shift_2") in assigned_pairs
    assert any(pair[1] == "shift_1" for pair in assigned_pairs)
