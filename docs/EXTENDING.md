# Extending the Scheduler

The scheduler is intentionally modular: constraint and objective helpers are pure functions that
operate on the loaded configuration, the current assignment state and the time index.

## Adding a new constraint

1. Implement a function under `modular_shift_scheduler/constraints.py` that inspects the assignment
   mapping (employee → shift list) and returns any useful metadata (e.g. hours worked, overlap pairs
   or shortage counts).
2. Call the helper from the solver or other helpers as appropriate. The solver is built as a
   branch-and-bound search, so prefer computations that can run incrementally.
3. Add a unit test under `tests/` that exercises the new logic directly.

When creating constraints, prefer reusing `TimeIndexer` for deriving durations or overlap information
instead of recomputing time arithmetic.

## Adding an objective term

1. Add a new helper in `modular_shift_scheduler/objectives.py` that computes a numerical contribution
   from the assignment or shortage dictionaries.
2. Combine it inside `total_objective` (or expose a new function if you want to select objective
   terms dynamically).
3. Cover the calculation with a targeted test verifying the contribution values.

## Configuration extensions

`SchedulingConfig` is a dataclass, so additional fields can be introduced with sensible defaults.
Remember to update `config.validate`, the Excel loader and the documentation in
`docs/CONFIG_REFERENCE.md` when doing so.
