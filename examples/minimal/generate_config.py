"""Generate the minimal example Excel workbook used in the documentation."""
from __future__ import annotations

from pathlib import Path

from modular_shift_scheduler.example_data import write_minimal_workbook


def main() -> int:
    target = Path(__file__).resolve().parent / "config.xlsx"
    write_minimal_workbook(target)
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":  # pragma: no cover - utility script
    raise SystemExit(main())
