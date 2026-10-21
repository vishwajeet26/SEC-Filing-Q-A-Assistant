"""Extract financial tables from SEC filing HTML."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

_FOOTER_TEXT_RE = re.compile(r"Form 10-K\s*\|", re.IGNORECASE)

_UNITS_RE = re.compile(
    r"\(?\s*in\s+(?:millions|thousands|billions|million|thousand|billion)[^)]{0,40}\)?",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class TableRow:
    cells: tuple[str, ...]


@dataclass(slots=True)
class ExtractedTable:
    table_index: int
    title: str | None
    units: str | None
    headers: tuple[str, ...]
    rows: list[TableRow] = field(default_factory=list)

    @property
    def markdown(self) -> str:
        lines: list[str] = []
        if self.headers:
            lines.append("| " + " | ".join(self.headers) + " |")
            lines.append("|" + "---|" * len(self.headers))
        for row in self.rows:
            cells = list(row.cells)
            if self.headers and len(cells) < len(self.headers):
                cells += [""] * (len(self.headers) - len(cells))
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)


def _cell_text(cell) -> str:
    return " ".join(cell.get_text(" ", strip=True).split())


def _table_is_layout(cells_per_row: list[int], text_cells: int, total_cells: int) -> bool:
    """Heuristic: layout tables are huge, mostly empty, or single-column wrappers."""
    if total_cells == 0:
        return True
    if len(cells_per_row) >= 8 and text_cells / max(total_cells, 1) < 0.35:
        return True
    if all(count <= 1 for count in cells_per_row):
        return True
    return False


def _title_and_units(table) -> tuple[str | None, str | None]:
    """Look at text immediately above the table for a caption and units note."""
    title: str | None = None
    units: str | None = None

    siblings: list[str] = []
    for sibling in table.find_all_previous(string=True):
        text = " ".join(str(sibling).split())
        if not text:
            continue
        siblings.append(text)
        if len(siblings) >= 4:
            break

    for text in siblings:
        if units is None:
            match = _UNITS_RE.search(text)
            if match:
                units = " ".join(match.group(0).split())
        if (
            title is None
            and 3 < len(text) < 220
            and not text.startswith("$")
            and not text.replace(",", "").replace(".", "").isdigit()
            and not _FOOTER_TEXT_RE.search(text)
        ):
            title = text
        if title is not None and units is not None:
            break

    if title is not None and units is not None and units.lower() in title.lower():
        title = _UNITS_RE.sub("", title).strip(" \t(),") or None
    return title, units


def extract_table_element(table) -> ExtractedTable | None:
    """Extract one <table> element; None when it looks like layout scaffolding."""
    cells_per_row: list[int] = []
    text_cells = 0
    total_cells = 0
    data_rows: list[tuple[str, ...]] = []

    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"], recursive=False) or tr.find_all(["td", "th"])
        texts = tuple(_cell_text(cell) for cell in cells)
        cells_per_row.append(len(texts))
        for value in texts:
            total_cells += 1
            if value:
                text_cells += 1
        if any(texts):
            data_rows.append(texts)

    if not data_rows:
        return None
    if _table_is_layout(cells_per_row, text_cells, total_cells):
        return None

    title, units = _title_and_units(table)
    headers = data_rows[0] if len(data_rows) > 1 else ()
    rows = (
        [TableRow(cells=row) for row in data_rows[1:]]
        if headers
        else [TableRow(cells=row) for row in data_rows]
    )

    return ExtractedTable(
        table_index=-1,  # assigned by the caller in document order
        title=title,
        units=units,
        headers=headers,
        rows=rows,
    )


def extract_sec_tables(html: str) -> list[ExtractedTable]:
    """Standalone entry point (tests): kept tables in document order."""
    soup = BeautifulSoup(html, "lxml")
    tables: list[ExtractedTable] = []
    for table in soup.find_all("table"):
        if table.find_parent("table") is not None:
            continue
        extracted = extract_table_element(table)
        if extracted is None:
            continue
        extracted.table_index = len(tables)
        tables.append(extracted)
    return tables
