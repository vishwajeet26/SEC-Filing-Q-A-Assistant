"""Load manifest.json filings into source_documents."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.database.models import SourceDocument
from app.database.session import get_session

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MANIFEST_PATH = DATA_DIR / "downloads" / "manifest.json"

_COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc.",
}


def load_manifest() -> list[dict[str, Any]]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            f"Manifest not found at {MANIFEST_PATH}. Run `uv run ../data/download.py` first."
        )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return manifest.get("filings", [])


def upsert_source_document(filing: dict[str, Any]) -> tuple[SourceDocument, bool]:
    """Insert or refresh one filing row. Returns (document, created)."""
    accession = filing["accession_number"]
    ticker = filing["ticker"]
    report_date = filing.get("report_date") or filing["filing_date"]
    with get_session() as session:
        document = session.scalar(
            select(SourceDocument).where(SourceDocument.accession_number == accession)
        )
        created = document is None
        if document is None:
            document = SourceDocument(accession_number=accession)
            session.add(document)

        document.ticker = ticker
        document.company_name = _COMPANY_NAMES.get(ticker, ticker)
        document.form = filing["form"]
        document.fiscal_year = int(report_date[:4])
        document.filing_date = date.fromisoformat(filing["filing_date"])
        document.report_date = date.fromisoformat(report_date) if report_date else None
        document.primary_document = filing.get("primary_document")
        document.source_url = filing.get("source_url")
        document.local_path = filing.get("local_path")

        session.commit()
        session.refresh(document)
        session.expunge(document)
        return document, created
