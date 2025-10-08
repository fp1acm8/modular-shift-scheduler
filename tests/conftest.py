from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from modular_shift_scheduler.example_data import minimal_config, write_minimal_workbook


@pytest.fixture()
def basic_config():
    return minimal_config()


@pytest.fixture()
def excel_fixture_path(tmp_path: Path, basic_config):
    path = tmp_path / "config.xlsx"
    write_minimal_workbook(path, config=basic_config)
    return path
