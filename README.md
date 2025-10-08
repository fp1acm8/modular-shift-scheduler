# Modular Shift Scheduler

A modular, constraint-based scheduling engine for workforce planning. The package reads a
lightweight Excel configuration and explores the search space of feasible assignments, producing
shift plans that respect skills, maximum working hours and overlapping shift constraints.

## Features

- 📊 **Excel-based configuration** – describe employees and shift demand in a spreadsheet.
- 🧠 **Composable optimisation** – each constraint/objective is expressed as a small helper
  function which keeps the solver easy to extend.
- 🛠️ **CLI and Python APIs** – use the command line to run ad-hoc schedules or import the package
  into larger applications.
- ✅ **Comprehensive test suite** – fixtures, unit tests and an end-to-end solver smoke test backed
  by Pytest.

## Installation

```bash
python -m pip install .
```

For development, install the optional tooling dependencies:

```bash
python -m pip install .[dev]
```

## Usage

### Command line

A minimal Excel workbook can be generated under `examples/minimal/config.xlsx`:

```bash
python examples/minimal/generate_config.py
```

Run the scheduler via the installed console script:

```bash
modular-shift-scheduler examples/minimal/config.xlsx --output schedule.json
```

The command prints a JSON summary of the solver status, assignments per employee and any shortages.

### Python API

```python
from modular_shift_scheduler import load_config_from_excel, solve

config = load_config_from_excel("examples/minimal/config.xlsx")
result = solve(config)

print(result.status, result.objective_value)
for employee, shifts in result.assignments.items():
    print(employee, shifts)
```

## Development

The project uses Ruff, Black, isort, mypy and pytest. All tools are configured in
`pyproject.toml`. A GitHub Actions workflow (`.github/workflows/ci.yml`) mirrors the local
experience by running formatting, linting, type-checking and the full test suite for Python 3.10 and
3.11.

Run the checks locally:

```bash
ruff check .
black --check .
isort --check-only .
mypy .
pytest
```

## Documentation

Additional documentation lives under `docs/`:

- `ARCHITECTURE.md` – high level view of the modules and data flow.
- `EXTENDING.md` – guidance on adding new constraints or objective terms.
- `CONFIG_REFERENCE.md` – specification of the Excel file expected by the loader.

## License

MIT License.
