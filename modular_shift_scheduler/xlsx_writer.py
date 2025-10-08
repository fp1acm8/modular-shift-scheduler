"""Utilities for emitting simple Excel workbooks without binary assets."""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence
from xml.etree import ElementTree as ET
import zipfile


def write_workbook(
    path: Path,
    *,
    employees_rows: Sequence[Sequence[object]],
    shifts_rows: Sequence[Sequence[object]] | None = None,
) -> None:
    """Write a minimal XLSX workbook containing ``Employees``/``Shifts`` sheets.

    The helper emits only the XML parts strictly required by the loader. Keeping the
    implementation in Python allows the repository to avoid committing binary Excel
    files while still providing reproducible fixtures and examples.
    """

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sheet1_xml = _sheet_xml(employees_rows)
    sheet2_xml = _sheet_xml(shifts_rows) if shifts_rows is not None else None

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml(sheet2_xml is not None))
        archive.writestr("_rels/.rels", _root_relationships_xml())
        archive.writestr("xl/workbook.xml", _workbook_xml(sheet2_xml is not None))
        archive.writestr("xl/_rels/workbook.xml.rels", _workbook_relationships_xml(sheet2_xml is not None))
        archive.writestr("xl/styles.xml", _styles_xml())
        archive.writestr("xl/worksheets/sheet1.xml", sheet1_xml)
        if sheet2_xml is not None:
            archive.writestr("xl/worksheets/sheet2.xml", sheet2_xml)


def _sheet_xml(rows: Sequence[Sequence[object]]) -> str:
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    root = ET.Element("worksheet", xmlns=ns)
    sheet_data = ET.SubElement(root, "sheetData")

    for row_idx, row in enumerate(rows, start=1):
        row_elem = ET.SubElement(sheet_data, "row", r=str(row_idx))
        for col_idx, value in enumerate(row, start=1):
            if value is None:
                continue
            column_letter = _column_letters(col_idx)
            cell = ET.SubElement(row_elem, "c", r=f"{column_letter}{row_idx}")
            if isinstance(value, str):
                cell.set("t", "inlineStr")
                is_elem = ET.SubElement(cell, "is")
                t_elem = ET.SubElement(is_elem, "t")
                t_elem.text = value
            else:
                v_elem = ET.SubElement(cell, "v")
                v_elem.text = str(value)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")


def _content_types_xml(include_second_sheet: bool) -> str:
    entries: List[str] = [
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    if include_second_sheet:
        entries.insert(
            4,
            '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>',
        )

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        + "".join(entries)
        + "</Types>"
    )


def _root_relationships_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>"
        "</Relationships>"
    )


def _workbook_xml(include_second_sheet: bool) -> str:
    sheets: List[str] = ['<sheet name="Employees" sheetId="1" r:id="rId1"/>']
    if include_second_sheet:
        sheets.append('<sheet name="Shifts" sheetId="2" r:id="rId2"/>')

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"
        "<sheets>"
        + "".join(sheets)
        + "</sheets></workbook>"
    )


def _workbook_relationships_xml(include_second_sheet: bool) -> str:
    entries: List[str] = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>',
    ]
    if include_second_sheet:
        entries.append(
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>',
        )
        style_id = "rId3"
    else:
        style_id = "rId2"
    entries.append(
        f'<Relationship Id="{style_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
    )

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        + "".join(entries)
        + "</Relationships>"
    )


def _styles_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
        "  <fonts count=\"1\"><font><sz val=\"11\"/><color theme=\"1\"/><name val=\"Calibri\"/><family val=\"2\"/></font></fonts>"
        "  <fills count=\"1\"><fill><patternFill patternType=\"none\"/></fill></fills>"
        "  <borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders>"
        "  <cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs>"
        "  <cellXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/></cellXfs>"
        "  <cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles>"
        "</styleSheet>"
    )


def _column_letters(index: int) -> str:
    result = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result
