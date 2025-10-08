"""Writers for exporting solver output."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from scheduler.data_models import AssignmentDecision, ScheduleSolution


class SolutionWriter:
    """Persist solutions to disk."""

    def __init__(self, output_dir: Path | str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def to_csv(self, solution: ScheduleSolution, filename: str = "schedule.csv") -> Path:
        """Write assignment decisions to a CSV file."""

        records = [decision.model_dump() for decision in solution.assignments if decision.is_assigned]
        df = pd.DataFrame.from_records(records)
        path = self.output_dir / filename
        df.to_csv(path, index=False)
        return path

    def to_excel(self, solution: ScheduleSolution, filename: str = "schedule.xlsx") -> Path:
        """Write assignment decisions to an Excel workbook."""

        path = self.output_dir / filename
        with pd.ExcelWriter(path) as writer:
            assignments = [decision.model_dump() for decision in solution.assignments]
            pd.DataFrame.from_records(assignments).to_excel(writer, sheet_name="assignments", index=False)
            pd.DataFrame.from_records([
                {"metric": key, "value": value} for key, value in solution.statistics.items()
            ]).to_excel(writer, sheet_name="metrics", index=False)
        return path


__all__ = ["SolutionWriter"]
