"""Run one hybrid search query against the corpus. Usage:

uv run python -m scripts.smoke_retrieval "iPhone Services revenue" --ticker AAPL
"""

from __future__ import annotations

import argparse

from app.retrieval.retriever import DocumentRetriever
from app.retrieval.types import SearchFilters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--ticker", default=None)
    parser.add_argument("--form", default=None)
    parser.add_argument("--years", default=None, help="comma-separated fiscal years")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    filters = SearchFilters(
        ticker=args.ticker,
        form=args.form,
        fiscal_years=[int(y) for y in args.years.split(",")] if args.years else None,
    )

    passages = DocumentRetriever().search(args.query, filters=filters, top_k=args.top_k)
    if not passages:
        print("No passages found.")
        return

    for passage in passages:
        print(f"[{passage.fusion_score:.4f}] {passage.ticker} {passage.form} FY{passage.fiscal_year} "
              f"chunk {passage.chunk_index} · {passage.section}")
        print(f"    {passage.text[:220].replace(chr(10), ' ')}…")
        print()


if __name__ == "__main__":
    main()
