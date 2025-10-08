"""Utilities for loading scheduling configuration from Excel workbooks."""
from __future__ import annotations

import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List
from xml.etree import ElementTree as ET

from .config import Employee, SchedulingConfig, ShiftDemand

NAMESPACE_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NAMESPACE_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
RELATIONSHIP_ATTR = (
    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
)


def _normalize_header(header: Iterable[str]) -> List[str]:
    return [str(cell).strip().lower().replace(" ", "_") for cell in header]


def load_config_from_excel(path: Path | str) -> SchedulingConfig:
    """Load a :class:`SchedulingConfig` from an Excel workbook."""

    sheets = _read_sheets(Path(path))
    try:
        employees_rows = sheets["employees"]
        shifts_rows = sheets["shifts"]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError("Workbook must contain 'Employees' and 'Shifts' sheets") from exc

    employees = _load_employees(tuple(tuple(row) for row in employees_rows))
    shifts = _load_shifts(tuple(tuple(row) for row in shifts_rows))

    config = SchedulingConfig(employees=employees, shifts=shifts)
    config.validate()
    return config


def _load_employees(rows: Iterable[tuple[object, ...]]) -> List[Employee]:
    iterator = iter(rows)
    header = _normalize_header(next(iterator, ()))
    required_columns = {"id", "name", "skills", "max_hours_per_week"}
    missing = required_columns - set(header)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(f"Employees sheet is missing required columns: {missing_str}")

    col_index = {label: idx for idx, label in enumerate(header)}
    employees: List[Employee] = []
    for row in iterator:
        if not any(row):
            continue
        identifier = str(row[col_index["id"]]).strip()
        name = str(row[col_index["name"]]).strip()
        skills_raw = row[col_index["skills"]] or ""
        if isinstance(skills_raw, str):
            skills = {skill for skill in skills_raw.split(",") if skill.strip()}
        else:
            skills = {str(skills_raw)} if skills_raw else set()
        max_hours = float(row[col_index["max_hours_per_week"]])
        cost_idx = col_index.get("cost_per_hour")
        cost = float(row[cost_idx]) if cost_idx is not None and row[cost_idx] is not None else 0.0
        employees.append(
            Employee(
                identifier=identifier,
                name=name,
                skills=skills,
                max_hours_per_week=max_hours,
                cost_per_hour=cost,
            )
        )
    if not employees:
        raise ValueError("Employees sheet must contain at least one employee")
    return employees


def _parse_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise TypeError(f"Unsupported datetime value: {value!r}")


def _load_shifts(rows: Iterable[tuple[object, ...]]) -> List[ShiftDemand]:
    iterator = iter(rows)
    header = _normalize_header(next(iterator, ()))
    required_columns = {"id", "start", "end", "required_skill", "required_employees"}
    missing = required_columns - set(header)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(f"Shifts sheet is missing required columns: {missing_str}")

    col_index = {label: idx for idx, label in enumerate(header)}
    shifts: List[ShiftDemand] = []
    for row in iterator:
        if not any(row):
            continue
        identifier = str(row[col_index["id"]]).strip()
        start = _parse_datetime(row[col_index["start"]])
        end = _parse_datetime(row[col_index["end"]])
        skill = str(row[col_index["required_skill"]])
        required = int(row[col_index["required_employees"]])
        weight_idx = col_index.get("weight")
        weight = (
            float(row[weight_idx]) if weight_idx is not None and row[weight_idx] is not None else 1.0
        )
        shifts.append(
            ShiftDemand(
                identifier=identifier,
                start=start,
                end=end,
                required_skill=skill,
                required_employees=required,
                weight=weight,
            )
        )
    if not shifts:
        raise ValueError("Shifts sheet must contain at least one row")
    return shifts


def _read_sheets(path: Path) -> Dict[str, List[List[object]]]:
    with zipfile.ZipFile(path, "r") as archive:
        workbook_xml = archive.read("xl/workbook.xml")
        workbook_root = ET.fromstring(workbook_xml)
        sheets = []
        for sheet in workbook_root.find(f"{NAMESPACE_MAIN}sheets").findall(
            f"{NAMESPACE_MAIN}sheet"
        ):
            name = sheet.attrib["name"].lower()
            relationship_id = sheet.attrib[RELATIONSHIP_ATTR]
            sheets.append((name, relationship_id))

        workbook_rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationships = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in workbook_rels_root.findall(f"{NAMESPACE_REL}Relationship")
        }

        shared_strings = _read_shared_strings(archive)

        parsed: Dict[str, List[List[object]]] = {}
        for name, relationship_id in sheets:
            target = relationships.get(relationship_id)
            if target is None:
                continue
            normalized_target = target.lstrip("/")
            if not normalized_target.startswith("xl/"):
                normalized_target = f"xl/{normalized_target}"
            data = archive.read(normalized_target)
            parsed[name] = _parse_sheet(data, shared_strings)
        return parsed


def _read_shared_strings(archive: zipfile.ZipFile) -> List[str]:
    try:
        data = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(data)
    strings = []
    for si in root.findall(f"{NAMESPACE_MAIN}si"):
        text_elem = si.find(f"{NAMESPACE_MAIN}t")
        if text_elem is None:
            # Some strings may contain rich text runs; concatenate their text nodes.
            text = "".join(
                node.text or ""
                for node in si.findall(f"{NAMESPACE_MAIN}r/{NAMESPACE_MAIN}t")
            )
        else:
            text = text_elem.text or ""
        strings.append(text)
    return strings


_COLUMN_REF_RE = re.compile(r"([A-Z]+)")


def _column_index(cell_reference: str) -> int:
    match = _COLUMN_REF_RE.match(cell_reference)
    if not match:
        raise ValueError(f"Invalid cell reference: {cell_reference}")
    letters = match.group(1)
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def _parse_sheet(data: bytes, shared_strings: List[str]) -> List[List[object]]:
    root = ET.fromstring(data)
    rows: List[List[object]] = []
    for row_elem in root.findall(f"{NAMESPACE_MAIN}sheetData/{NAMESPACE_MAIN}row"):
        values: Dict[int, object] = {}
        for cell in row_elem.findall(f"{NAMESPACE_MAIN}c"):
            reference = cell.attrib.get("r")
            if reference is None:
                continue
            column = _column_index(reference)
            cell_type = cell.attrib.get("t")
            value = _parse_cell(cell, cell_type, shared_strings)
            values[column] = value
        row_values = []
        max_index = max(values) if values else -1
        for idx in range(max_index + 1):
            row_values.append(values.get(idx))
        rows.append(row_values)
    return rows


def _parse_cell(
    cell: ET.Element, cell_type: str | None, shared_strings: List[str]
) -> object | None:
    if cell_type == "s":
        index_elem = cell.find(f"{NAMESPACE_MAIN}v")
        if index_elem is None or index_elem.text is None:
            return None
        return shared_strings[int(index_elem.text)]
    if cell_type == "inlineStr":
        text_elem = cell.find(f"{NAMESPACE_MAIN}is/{NAMESPACE_MAIN}t")
        return text_elem.text if text_elem is not None else ""
    value_elem = cell.find(f"{NAMESPACE_MAIN}v")
    if value_elem is None or value_elem.text is None:
        return None
    raw_value = value_elem.text
    if raw_value.isdigit():
        return int(raw_value)
    try:
        return float(raw_value)
    except ValueError:
        return raw_value
