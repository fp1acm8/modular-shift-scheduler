"""Helpers for discretising time into slots used by the solver."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Tuple

from .config import ShiftDemand


@dataclass(slots=True)
class TimeIndexer:
    """Maps datetimes to slot indices based on a fixed interval."""

    start: datetime
    end: datetime
    slot_minutes: int

    @classmethod
    def from_shifts(cls, shifts: Iterable[ShiftDemand], slot_minutes: int) -> "TimeIndexer":
        start = min(shift.start for shift in shifts)
        end = max(shift.end for shift in shifts)
        return cls(start=start, end=end, slot_minutes=slot_minutes)

    @property
    def slot_delta(self) -> timedelta:
        return timedelta(minutes=self.slot_minutes)

    def slots_between(self, start: datetime, end: datetime) -> Tuple[int, int]:
        if start < self.start or end > self.end:
            raise ValueError("Range is outside of configured horizon")
        start_idx = self.index(start)
        end_idx = self.index(end)
        if end_idx <= start_idx:
            raise ValueError("End must occur after start")
        return start_idx, end_idx

    def index(self, timestamp: datetime) -> int:
        if timestamp < self.start or timestamp > self.end:
            raise ValueError("Timestamp is outside of index range")
        delta = timestamp - self.start
        steps, remainder = divmod(delta, self.slot_delta)
        if remainder:
            raise ValueError("Timestamp must align with slot boundaries")
        return int(steps)

    def duration_in_hours(self, start: datetime, end: datetime) -> float:
        start_idx, end_idx = self.slots_between(start, end)
        slots = end_idx - start_idx
        return slots * (self.slot_minutes / 60)

    def duration_for_shift(self, shift: ShiftDemand) -> float:
        return self.duration_in_hours(shift.start, shift.end)

    def num_slots(self) -> int:
        total_slots, remainder = divmod(self.end - self.start, self.slot_delta)
        if remainder:
            raise ValueError("Total range must align with slot boundaries")
        return int(total_slots)
