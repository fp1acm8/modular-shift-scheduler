# Modular Shift Scheduler

A modular, constraint-based scheduling engine for workforce planning.

## Features

- Configurable ingestion of workforce data from Excel workbooks with validation.
- Pydantic data models for employees, availability, and demand profiles.
- OR-Tools CP-SAT backend with pluggable hard and soft constraints and objective terms.
- Solver orchestration pipeline with rich reporting on key performance indicators.
- Typer-powered CLI for solving, validating, explaining configuration, and exporting schedules.

## Getting Started

```bash
pip install -e .
```

Then run the CLI:

```bash
scheduler solve path/to/config.yaml path/to/workbook.xlsx
```

## Development

Install development dependencies and enable pre-commit hooks:

```bash
pip install -e .[dev]
pre-commit install
```
