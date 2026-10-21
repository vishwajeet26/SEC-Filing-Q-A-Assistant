"""Pydantic models shared by retrieval and agent tools."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

MAX_PASSAGE_EXCERPT_CHARS = 800
MAX_AGENT_OUTPUT_CHARS = 12_000


class SearchFilters(BaseModel):
    ticker: str | None = None
    fiscal_years: list[int] | None = None
    form: str | None = None


class RankedChunkHit(BaseModel):
    chunk_id: UUID
    rank: int
    score: float | None = None


class RetrievedPassage(BaseModel):
    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    text: str
    page: str | None
    section: str | None
    fusion_score: float
    ticker: str
    company_name: str
    form: str
    filing_date: date
    fiscal_year: int | None = None
    accession_number: str | None = None
    neighbors: list[RetrievedPassage] = []


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _passage_header(passage: RetrievedPassage) -> str:
    bits = [passage.ticker, passage.form]
    if passage.fiscal_year is not None:
        bits.append(f"FY{passage.fiscal_year}")
    if passage.section:
        bits.append(f"section: {passage.section}")
    if passage.page:
        bits.append(f"page: {passage.page}")
    return " · ".join(bits)


def format_passages_for_agent(passages: list[RetrievedPassage]) -> str:
    """Render passages (with optional neighbors) for the LLM tool response."""
    if not passages:
        return "No passages found."

    blocks: list[str] = []
    for passage in passages:
        lines = [
            f"### chunk_id: {passage.chunk_id}",
            _passage_header(passage),
            f"chunk_index: {passage.chunk_index}",
            "",
            _clip(passage.text, MAX_AGENT_OUTPUT_CHARS),
        ]
        for neighbor in passage.neighbors:
            role = "before" if neighbor.chunk_index < passage.chunk_index else "after"
            lines += [
                "",
                f"--- neighbor ({role}) chunk_id: {neighbor.chunk_id} · "
                f"chunk_index: {neighbor.chunk_index} ---",
                _clip(neighbor.text, MAX_AGENT_OUTPUT_CHARS),
            ]
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)
