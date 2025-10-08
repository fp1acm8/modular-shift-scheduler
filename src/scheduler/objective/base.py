"""Objective term interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Protocol

from scheduler.data_models import SchedulingInputs
from scheduler.time_index import TimeSlot


class BackendProtocol(Protocol):
    def get_variable(self, employee_id: str, slot_index: int): ...
    def add_weighted_sum(self, terms, weight: float, name: str): ...


class ObjectiveTerm(ABC):
    """Soft objective term."""

    name: str

    def __init__(self, name: str, weight: float) -> None:
        self.name = name
        self.weight = weight

    @abstractmethod
    def apply(self, backend: BackendProtocol, inputs: SchedulingInputs, slots: Iterable[TimeSlot]) -> None:
        """Register the objective contribution."""


__all__ = ["ObjectiveTerm"]
