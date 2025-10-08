"""Typer CLI entrypoints."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import logging

import typer
from rich.console import Console

from scheduler import reporting
from scheduler.config import AppConfig
from scheduler.io.excel_loader import ExcelDataLoader
from scheduler.io.writers import SolutionWriter
from scheduler.logging_utils import configure_logging
from scheduler.optimizer.solver import SolverOrchestrator
from scheduler.utils import load_config

app = typer.Typer(help="Constraint-based workforce scheduling CLI")
console = Console()


def _override_config(config: AppConfig, workbook: Path | None, output: Path | None) -> AppConfig:
    data = config.model_dump()
    if workbook is not None:
        data.setdefault("files", {})
        data["files"]["workbook_path"] = str(workbook)
    if output is not None:
        data.setdefault("files", {})
        data["files"]["output_path"] = str(output)
    return AppConfig(**data)


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging")) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    configure_logging(level=level)


@app.command()
def solve(config_path: Path, workbook: Optional[Path] = typer.Option(None), output: Optional[Path] = typer.Option(None)) -> None:
    """Solve the scheduling problem and print a summary."""

    config = load_config(config_path)
    config = _override_config(config, workbook, output)
    orchestrator = SolverOrchestrator(config, base_dir=config_path.parent)
    solution = orchestrator.solve()
    reporting.print_report(solution)


@app.command("validate-data")
def validate_data(config_path: Path, workbook: Optional[Path] = typer.Option(None)) -> None:
    """Validate the input workbook without solving."""

    config = load_config(config_path)
    config = _override_config(config, workbook, None)
    loader = ExcelDataLoader(config.files.workbook_path)
    inputs = loader.load()
    console.print(f"Loaded {len(inputs.employees)} employees and {len(inputs.demand)} demand intervals")


@app.command()
def explain(config_path: Path) -> None:
    """Explain the active configuration."""

    config = load_config(config_path)
    console.print(reporting.explain_configuration(config))


@app.command()
def export(
    config_path: Path,
    workbook: Optional[Path] = typer.Option(None),
    output: Path = typer.Option(..., help="Directory to store exported schedule"),
    excel: bool = typer.Option(False, help="Export Excel instead of CSV"),
) -> None:
    """Solve and export the schedule."""

    config = load_config(config_path)
    config = _override_config(config, workbook, output)
    orchestrator = SolverOrchestrator(config, base_dir=config_path.parent)
    solution = orchestrator.solve()
    writer = SolutionWriter(output)
    path = writer.to_excel(solution) if excel else writer.to_csv(solution)
    console.print(f"Exported schedule to {path}")


__all__ = ["app"]
