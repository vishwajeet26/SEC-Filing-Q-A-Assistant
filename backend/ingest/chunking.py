"""Chunking for SEC HTML filings.

Parse the filing once with BeautifulSoup: kept financial tables are replaced by
in-order `[[TABLE:n]]` markers in the narrative text (so section context and
position survive), and are extracted separately as row-group chunks with the
header repeated and the full table kept in metadata for citation display.
Narrative blocks are packed into ~512-token chunks with `Item` headings tracked
as section metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import warnings

from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from ingest.sec_tables import ExtractedTable, extract_table_element

CHUNK_MAX_TOKENS = 512
TABLE_ROW_GROUP_ROWS = 12

_MARKER_RE = re.compile(r"\[\[TABLE:(\d+)\]\]")
_ITEM_FIND_RE = re.compile(r"^Item\s+[0-9]+[A-Z]?\.?", re.IGNORECASE)
_FOOTER_RE = re.compile(r"\|\s*\d+\s*$")

_encoder = None
_encoder_failed = False


@dataclass(frozen=True, slots=True)
class ChunkRecord:
    chunk_index: int
    text: str
    page: str | None
    section: str | None
    token_count: int
    chunk_metadata: dict[str, Any]


def count_tokens(text: str) -> int:
    """tiktoken cl100k when available; word-count approximation otherwise."""
    global _encoder, _encoder_failed
    if not _encoder_failed:
        if _encoder is None:
            try:
                import tiktoken

                _encoder = tiktoken.get_encoding("cl100k_base")
            except Exception:
                _encoder_failed = True
        if _encoder is not None:
            return len(_encoder.encode(text, allowed_special=set(), disallowed_special=()))
    return max(1, int(len(text.split()) * 1.3))


def parse_filing(html: str) -> tuple[str, list[ExtractedTable]]:
    """Return (marked narrative text, kept tables) with matching marker indexes."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "head", "ix:header"]):
        tag.decompose()

    kept: list[tuple[Any, ExtractedTable]] = []
    for table in soup.find_all("table"):
        if table.find_parent("table") is not None:
            continue
        extracted = extract_table_element(table)
        if extracted is None:
            continue
        kept.append((table, extracted))

    for index, (element, extracted) in enumerate(kept):
        extracted.table_index = index
        element.replace_with(f"\n[[TABLE:{index}]]\n")

    return soup.get_text("\n"), [extracted for _, extracted in kept]


def _normalize_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            continue
        blocks.append(line)
    return blocks


def _section_for(block: str, current: str | None) -> str | None:
    match = _ITEM_FIND_RE.search(block.strip())
    if match and len(block) < 120:
        return match.group(0).rstrip(".").strip()
    return current


def _filing_metadata_base(filing_metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": filing_metadata.get("ticker"),
        "company_name": filing_metadata.get("company_name"),
        "form": filing_metadata.get("form"),
        "fiscal_year": filing_metadata.get("fiscal_year"),
        "filing_date": filing_metadata.get("filing_date"),
        "accession_number": filing_metadata.get("accession_number"),
    }


def _table_row_chunk_text(table: ExtractedTable, row_group: list[int]) -> str:
    header_line = " | ".join(table.headers) if table.headers else ""
    title_line = table.title or f"Table {table.table_index + 1}"
    units_line = f" ({table.units})" if table.units else ""
    lines = [f"{title_line}{units_line}"]
    if header_line:
        lines.append(header_line)
    for row_index in row_group:
        lines.append(" | ".join(table.rows[row_index].cells))
    return "\n".join(lines)


def chunk_filing(
    html: str,
    filing_metadata: dict[str, Any],
    *,
    max_tokens: int = CHUNK_MAX_TOKENS,
    max_chunks: int | None = None,
) -> list[ChunkRecord]:
    marked_text, tables = parse_filing(html)
    blocks = _normalize_blocks(marked_text)

    records: list[ChunkRecord] = []
    base_meta = _filing_metadata_base(filing_metadata)
    used_table_indexes: set[int] = set()

    current_section: str | None = None
    buffer: list[str] = []
    buffer_tokens = 0

    def flush() -> None:
        nonlocal buffer, buffer_tokens
        if not buffer:
            return
        if max_chunks is not None and len(records) >= max_chunks:
            buffer, buffer_tokens = [], 0
            return
        text = "\n".join(buffer)
        records.append(
            ChunkRecord(
                chunk_index=len(records),
                text=text,
                page=None,
                section=current_section,
                token_count=count_tokens(text),
                chunk_metadata={**base_meta, "chunk_kind": "narrative", "raw_text": text},
            )
        )
        buffer, buffer_tokens = [], 0

    for block in blocks:
        current_section = _section_for(block, current_section)
        marker = _MARKER_RE.fullmatch(block.strip())
        if marker:
            flush()
            table_index = int(marker.group(1))
            if table_index < len(tables):
                _append_table_records(
                    records=records,
                    table=tables[table_index],
                    base_meta=base_meta,
                    max_tokens=max_tokens,
                    max_chunks=max_chunks,
                )
                used_table_indexes.add(table_index)
            continue

        block_tokens = count_tokens(block)
        if buffer and buffer_tokens + block_tokens > max_tokens:
            flush()
        buffer.append(block)
        buffer_tokens += block_tokens

    flush()

    # Safety net: tables whose marker didn't survive text extraction.
    if max_chunks is None:
        for table in tables:
            if table.table_index in used_table_indexes:
                continue
            _append_table_records(
                records=records,
                table=table,
                base_meta=base_meta,
                max_tokens=max_tokens,
                max_chunks=max_chunks,
            )

    return records


def _append_table_records(
    *,
    records: list[ChunkRecord],
    table: ExtractedTable,
    base_meta: dict[str, Any],
    max_tokens: int,
    max_chunks: int | None,
) -> None:
    if not table.rows:
        return

    groups: list[list[int]] = []
    current: list[int] = []
    current_tokens = count_tokens(_table_row_chunk_text(table, []))
    for row_index in range(len(table.rows)):
        row_tokens = count_tokens(" | ".join(table.rows[row_index].cells))
        if current and (
            len(current) >= TABLE_ROW_GROUP_ROWS or current_tokens + row_tokens > max_tokens
        ):
            groups.append(current)
            current = []
            current_tokens = count_tokens(_table_row_chunk_text(table, []))
        current.append(row_index)
        current_tokens += row_tokens
    if current:
        groups.append(current)

    table_meta = {
        "table_index": table.table_index,
        "title": table.title,
        "units": table.units,
        "markdown": table.markdown,
    }

    for group in groups:
        if max_chunks is not None and len(records) >= max_chunks:
            return
        text = _table_row_chunk_text(table, group)
        records.append(
            ChunkRecord(
                chunk_index=len(records),
                text=text,
                page=None,
                section=table.title,
                token_count=count_tokens(text),
                chunk_metadata={
                    **base_meta,
                    "chunk_kind": "table_row",
                    "table": table_meta,
                    "row_numbers": group,
                },
            )
        )


def extract_filing_text(html: str) -> str:
    """Normalized narrative text for `source_documents.content_text`."""
    marked_text, _tables = parse_filing(html)
    blocks = _normalize_blocks(marked_text)
    kept: list[str] = []
    for block in blocks:
        if _MARKER_RE.fullmatch(block.strip()):
            kept.append("[table]")
            continue
        kept.append(block)
    return "\n".join(kept)
