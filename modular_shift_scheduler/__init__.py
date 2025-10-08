"""Public package interface for the modular shift scheduler."""
from .config import Employee, SchedulingConfig, ShiftDemand
from .excel_loader import load_config_from_excel
from .example_data import minimal_config, write_minimal_workbook
from .solver import SolveResult, solve

__all__ = [
    "Employee",
    "SchedulingConfig",
    "ShiftDemand",
    "minimal_config",
    "SolveResult",
    "load_config_from_excel",
    "write_minimal_workbook",
    "solve",
]
