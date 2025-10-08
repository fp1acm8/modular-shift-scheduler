"""Constraint interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Protocol

from scheduler.data_models import SchedulingInputs
from scheduler.time_index import TimeSlot


class BackendProtocol(Protocol):
    def get_variable(self, employee_id: str, slot_index: int): ...
    def add_constraint(self, *args, **kwargs): ...


class Constraint(ABC):
    """Base constraint interface."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def apply(self, backend: BackendProtocol, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:
        """Apply the constraint to the backend."""


__all__ = ["Constraint", "BackendProtocol"]
