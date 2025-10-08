"""Logging helpers."""
from __future__ import annotations

import logging
from typing import Optional

from rich.logging import RichHandler


def configure_logging(level: int = logging.INFO, enable_rich: bool = True) -> None:
    """Configure logging for CLI usage."""

    handlers = None
    if enable_rich:
        handlers = [RichHandler(rich_tracebacks=True)]
    logging.basicConfig(level=level, handlers=handlers, format="%(message)s")


__all__ = ["configure_logging"]
