from app.retrieval.keywords import (
    _apply_word_budget,
    extract_fts_keywords,
)
from app.retrieval.types import SearchFilters


def test_fast_path_short_query_untouched():
    query = "iPhone Services revenue"
    assert extract_fts_keywords(query) == query


def test_deterministic_fallback_strips_filler_and_company():
    query = "How did Apple describe the change in Services revenue across its filings?"
    result = extract_fts_keywords(query, filters=SearchFilters(ticker="AAPL"))
    words = result.split()
    assert "How" not in words and "did" not in words and "the" not in words
    assert "Apple" not in words
    assert len(words) <= 5
    assert "Services" in words and "revenue" in words


def test_word_budget_caps_length():
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta"]
    kept = _apply_word_budget(words)
    assert len(kept) == 5
    assert kept == words[:5]


def test_empty_query_passthrough():
    assert extract_fts_keywords("   ") == ""
