"""Ingest the downloaded corpus: filings → chunks → embeddings.

Run with `uv run python -m ingest.corpus` from `backend/`. Idempotent per
filing: existing chunks for a filing are replaced.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from sqlalchemy import delete, func, select, update

from app.config import settings
from app.database.models import DocumentChunk, SourceDocument
from app.database.session import get_session
from ingest.chunking import chunk_filing, extract_filing_text
from ingest.embeddings import embed_texts
from ingest.load_source_documents import DATA_DIR, load_manifest, upsert_source_document


def _filing_html(filing: dict) -> Path:
    local = filing.get("local_path")
    if not local:
        raise FileNotFoundError(f"Filing {filing['accession_number']} has no local_path")
    path = DATA_DIR / "downloads" / local
    if not path.is_file():
        raise FileNotFoundError(f"Missing filing HTML: {path}")
    return path


def ingest_filing(filing: dict, *, chunk_batch: int = 200) -> int:
    document, created = upsert_source_document(filing)
    html = _filing_html(filing).read_text(encoding="utf-8", errors="replace")

    filing_metadata = {
        "ticker": document.ticker,
        "company_name": document.company_name,
        "form": document.form,
        "fiscal_year": document.fiscal_year,
        "filing_date": document.filing_date.isoformat(),
        "accession_number": document.accession_number,
    }

    records = chunk_filing(html, filing_metadata)

    with get_session() as session:
        session.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document.id)
        )
        session.execute(
            update(SourceDocument)
            .where(SourceDocument.id == document.id)
            .values(content_text=extract_filing_text(html))
        )
        session.commit()

    inserted = 0
    for start in range(0, len(records), chunk_batch):
        batch = records[start : start + chunk_batch]
        embeddings = embed_texts([record.text for record in batch])
        rows = [
            DocumentChunk(
                document_id=document.id,
                chunk_index=record.chunk_index,
                text=record.text,
                page=record.page,
                section=record.section,
                token_count=record.token_count,
                chunk_metadata=record.chunk_metadata,
                embedding=embedding,
            )
            for record, embedding in zip(batch, embeddings, strict=True)
        ]
        with get_session() as session:
            session.add_all(rows)
            session.commit()
        inserted += len(batch)

    with get_session() as session:
        session.execute(
            update(SourceDocument)
            .where(SourceDocument.id == document.id)
            .values(chunk_count=inserted)
        )
        session.commit()

    return inserted


def main() -> int:
    filings = load_manifest()
    if not filings:
        print("No filings in manifest. Run `uv run ../data/download.py` first.")
        return 1

    print(f"Ingesting {len(filings)} filing(s) — mode: {'demo' if settings.is_demo else 'real'}")
    for filing in filings:
        started = time.perf_counter()
        try:
            inserted = ingest_filing(filing)
        except FileNotFoundError as exc:
            print(f"  SKIP {filing.get('ticker')} {filing.get('filing_date')}: {exc}")
            continue
        elapsed = time.perf_counter() - started
        print(
            f"  {filing['ticker']} {filing['form']} FY{str(filing.get('report_date'))[:4]} "
            f"({filing['filing_date']}): {inserted} chunks in {elapsed:.1f}s"
        )

    with get_session() as session:
        documents = session.scalar(select(func.count(SourceDocument.id))) or 0
        chunks = session.scalar(select(func.count(DocumentChunk.id))) or 0
    print(f"Corpus ready: {documents} documents, {chunks} chunks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
