# Architecture

The modular shift scheduler is organised as a small collection of focused modules:

| Module | Responsibility |
| ------ | -------------- |
| `config` | Data classes describing employees, shift demand and solver options. |
| `excel_loader` | Translates a structured Excel workbook into `SchedulingConfig`. |
| `time_index` | Discretises the planning horizon into fixed-width slots. |
| `constraints` | Provides helper functions for coverage, hour usage and overlap checks. |
| `objectives` | Computes labour cost, shortage penalties and total objective values. |
| `solver` | Performs a depth-first branch-and-bound search to find the best assignment. |
| `cli` | Minimal command line entry point for ad-hoc scheduling runs. |

## Data flow

1. Input data is authored in Excel using the schema described in `CONFIG_REFERENCE.md`.
2. `load_config_from_excel` loads employees and shift rows into dataclasses and performs validation.
3. `solve` constructs the time index, candidate employee lists and recursive search state.
4. Constraint helpers are consulted at each branch to enforce coverage, max-hours and non-overlap rules.
5. Objective helpers compute labour cost and shortage penalties for pruning and ranking.
6. The branch-and-bound search finds the best assignment and `SolveResult` materialises the final schedule and shortages.

## Extensibility

Each constraint and objective is expressed as a pure function that accepts the problem, configuration
and variable dictionaries. New rules can therefore be added without modifying the solver core; see
`EXTENDING.md` for guidance.
