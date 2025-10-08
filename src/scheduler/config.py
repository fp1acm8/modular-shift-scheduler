"""Configuration models and helpers for the scheduler application."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, BaseSettings, Field, PositiveInt, validator


class SolverToggles(BaseModel):
    """Enable or disable individual hard constraints."""

    enforce_coverage: bool = True
    enforce_max_hours: bool = True
    enforce_daily_limits: bool = True
    enforce_rest_periods: bool = False
    balance_weekend_shifts: bool = False


class ObjectiveWeights(BaseModel):
    """Weights for soft objective terms."""

    honor_preferences: float = 1.0
    distribute_weekends: float = 0.5
    minimize_overtime: float = 0.25

    @validator("honor_preferences", "distribute_weekends", "minimize_overtime")
    def non_negative(cls, value: float) -> float:  # noqa: D417
        if value < 0:
            raise ValueError("Objective weights must be non-negative")
        return value


class TimeSettings(BaseModel):
    """Settings controlling time indexing."""

    start_date: str = Field(..., description="ISO date for the planning horizon start")
    end_date: str = Field(..., description="ISO date for the planning horizon end")
    slot_minutes: PositiveInt = Field(60, description="Length of a time slot in minutes")
    timezone: str = Field("UTC", description="Timezone identifier")


class FileSettings(BaseModel):
    """Paths to input and output artefacts."""

    workbook_path: Path = Field(..., description="Path to the source Excel workbook")
    output_path: Optional[Path] = Field(None, description="Destination for exported schedules")


class SolverSettings(BaseModel):
    """Solver parameter configuration."""

    time_limit_seconds: Optional[int] = Field(None, ge=1)
    log_search_progress: bool = False
    num_workers: Optional[int] = Field(None, ge=1)


class AppConfig(BaseSettings):
    """Top-level configuration for the scheduling application."""

    time: TimeSettings
    files: FileSettings
    solver: SolverSettings = SolverSettings()
    toggles: SolverToggles = SolverToggles()
    objective: ObjectiveWeights = ObjectiveWeights()

    class Config:
        env_prefix = "SCHEDULER_"
        env_nested_delimiter = "__"

    @classmethod
    def load(cls, path: Path | str) -> "AppConfig":
        """Load configuration from a JSON or YAML file."""

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)

        text = path.read_text()
        suffix = path.suffix.lower()

        if suffix in {".yaml", ".yml"}:
            import yaml

            data: Dict[str, object] = yaml.safe_load(text) or {}
        elif suffix == ".json":
            import json

            data = json.loads(text)
        else:
            raise ValueError(f"Unsupported config format: {suffix}")

        return cls(**data)


def resolve_paths(config: AppConfig, base_dir: Optional[Path] = None) -> AppConfig:
    """Return a copy of ``config`` with paths resolved relative to ``base_dir``."""

    base_dir = base_dir or Path.cwd()
    data = config.model_dump()

    files: Dict[str, object] = data.get("files", {})
    for key in ("workbook_path", "output_path"):
        value = files.get(key)
        if value is not None:
            files[key] = str((base_dir / value).resolve())
    data["files"] = files

    return AppConfig(**data)


__all__ = [
    "AppConfig",
    "FileSettings",
    "ObjectiveWeights",
    "SolverSettings",
    "SolverToggles",
    "TimeSettings",
    "resolve_paths",
]
