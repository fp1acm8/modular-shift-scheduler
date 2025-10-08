"""Time indexing helpers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Sequence

import pandas as pd


@dataclass(frozen=True)
class TimeSlot:
    """Discrete time slot used by the solver."""

    index: int
    start: datetime
    end: datetime

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600


class TimeIndexer:
    """Build time slots for the planning horizon."""

    def __init__(self, start: datetime, end: datetime, slot_minutes: int) -> None:
        if end <= start:
            raise ValueError("End must be after start")
        self.start = start
        self.end = end
        self.slot_minutes = slot_minutes
        self._slots: List[TimeSlot] = []

    def build(self) -> List[TimeSlot]:
        if self._slots:
            return self._slots

        delta = timedelta(minutes=self.slot_minutes)
        index = 0
        cursor = self.start
        while cursor < self.end:
            slot_end = min(cursor + delta, self.end)
            self._slots.append(TimeSlot(index=index, start=cursor, end=slot_end))
            index += 1
            cursor = slot_end
        return self._slots

    def as_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "index": [slot.index for slot in self.build()],
                "start": [slot.start for slot in self.build()],
                "end": [slot.end for slot in self.build()],
            }
        )

    def find_slot(self, moment: datetime) -> TimeSlot:
        for slot in self.build():
            if slot.start <= moment < slot.end:
                return slot
        raise KeyError(moment)


__all__ = ["TimeIndexer", "TimeSlot"]
