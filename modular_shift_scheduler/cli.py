"""Command line interface for running the shift scheduler."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from . import load_config_from_excel, solve


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve a workforce schedule")
    parser.add_argument("config", type=Path, help="Path to Excel configuration file")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the resulting schedule as JSON",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config_from_excel(args.config)
    result = solve(config)

    report: Dict[str, Any] = {
        "status": result.status,
        "objective_value": result.objective_value,
        "assignments": result.assignments,
        "shortages": result.shortage_by_shift,
    }

    if args.output:
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
