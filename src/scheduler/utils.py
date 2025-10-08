"""Miscellaneous utilities for the scheduler."""
from __future__ import annotations

from pathlib import Path

from scheduler.config import AppConfig


def load_config(path: str | Path) -> AppConfig:
    """Load configuration from disk."""

    return AppConfig.load(path)


__all__ = ["load_config"]
