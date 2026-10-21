"""Extractive demo agent — the keyless stand-in for the LLM agent.

It follows the same contract as the PydanticAI agent: retrieve passages with the
same tools, register them in the turn registry, and return a `GroundedAnswer`
whose citations quote the retrieved chunks verbatim. Instead of generating
prose it extracts and quotes the most query-relevant sentences, so the full
pipeline — retrieval, citations, grounding, streaming — can be exercised
without an OpenAI key.
"""

from __future__ import annotations

import re
import time

from app.assistant.deps import DocumentAgentDeps
from app.assistant.outputs import Citation, GroundedAnswer
from app.assistant.status import emit_agent_done, emit_agent_start
from app.assistant.tools import _search_sync
from app.retrieval.types import RetrievedPassage

INSUFFICIENT_EVIDENCE_ANSWER = (
    "I could not find enough evidence in the corpus to answer this question. "
    "Try naming a company (e.g. Apple, NVIDIA) or a filing period, or rephrase "
    "with more specific terms."
)

_COMPANY_TICKERS = {
    "apple": "AAPL",
    "microsoft": "MSFT",
    "nvidia": "NVDA",
    "amazon": "AMZN",
    "alphabet": "GOOGL",
    "google": "GOOGL",
}

_STOPWORDS = frozenset(
    """a an and are as at be by did do does for from how in is it its of on or
    that the their them they this to was were what when which who whose with
    about across between describe described describes explain compare change
    changed changes tell give show across filings filing""".split()
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z0-9]+")

# Generic temporal/corporate tokens: useful for retrieval, useless for picking
# which sentence to quote.
_SENTENCE_GENERIC = frozenset(
    {"fiscal", "annual", "quarter", "quarterly", "year", "years", "company", "corporation", "form"}
)

MAX_SELECTED_PASSAGES = 3


def _content_tokens(text: str) -> list[str]:
    return [t for t in _WORD.findall(text.lower()) if t not in _STOPWORDS and len(t) > 2]


def _filters_from_query(query: str):
    from app.retrieval.types import SearchFilters

    lowered = query.lower()
    ticker = None
    for name, tick in _COMPANY_TICKERS.items():
        if re.search(rf"\b{name}\b", lowered):
            ticker = tick
            break
    years = [int(y) for y in re.findall(r"\b(20[12]\d)\b", query)]
    form = "10-Q" if re.search(r"\b10-?q\b", lowered) else None
    return SearchFilters(ticker=ticker, fiscal_years=years or None, form=form)


def _token_weights(passages: list[RetrievedPassage], query_tokens: list[str]) -> dict[str, float]:
    """Down-weight query tokens that appear in most retrieved passages — they
    don't discriminate (e.g. 'fiscal', '2025', the company name)."""
    if not passages:
        return {token: 1.0 for token in query_tokens}
    texts = [re.sub(r"\s+", " ", p.text).lower() for p in passages]
    weights: dict[str, float] = {}
    for token in query_tokens:
        presence = sum(1 for text in texts if token in text)
        fraction = presence / len(texts)
        weights[token] = 0.25 if fraction > 0.6 else 1.0
    return weights


def _coverage(passage: RetrievedPassage, query_tokens: list[str], weights: dict[str, float]) -> float:
    text = set(_WORD.findall(passage.text.lower()))
    return sum(weight for token, weight in weights.items() if token in text)


def _select_passages(
    passages: list[RetrievedPassage],
    query_tokens: list[str],
) -> list[RetrievedPassage]:
    weights = _token_weights(passages, query_tokens)
    ranked = sorted(
        passages,
        key=lambda p: (_coverage(p, query_tokens, weights), p.fusion_score),
        reverse=True,
    )

    distinct_documents = {p.document_id for p in ranked}
    max_per_document = 1 if len(distinct_documents) > 1 else MAX_SELECTED_PASSAGES

    per_document: dict[str, int] = {}
    selected: list[RetrievedPassage] = []
    for passage in ranked:
        count = per_document.get(passage.document_id, 0)
        if count >= max_per_document or len(selected) >= MAX_SELECTED_PASSAGES:
            continue
        per_document[passage.document_id] = count + 1
        selected.append(passage)
        if len(selected) >= MAX_SELECTED_PASSAGES:
            break

    # When coverage is weak everywhere, fall back to fusion order.
    if selected and max(_coverage(p, query_tokens, weights) for p in selected) < 0.5:
        return passages[:MAX_SELECTED_PASSAGES]
    return selected


def _best_sentences(
    passage: RetrievedPassage,
    query_tokens: list[str],
    weights: dict[str, float],
    limit: int,
    *,
    min_weight: float = 1.0,
) -> list[str]:
    text = re.sub(r"\s+", " ", passage.text).strip()
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if len(s.strip()) >= 40]
    if not sentences:
        return [text[:320]] if text else []

    def weight_of(sentence: str) -> float:
        tokens = set(_WORD.findall(sentence.lower()))
        return sum(
            weights.get(token, 1.0)
            for token in query_tokens
            if token in tokens and token not in _SENTENCE_GENERIC
        )

    def score(sentence: str) -> float:
        weight = weight_of(sentence)
        length_penalty = max(len(sentence), 120) / 120
        return (weight * weight) / length_penalty

    substantive = [s for s in sentences if weight_of(s) >= min_weight]
    if not substantive:
        return []
    ranked = sorted(substantive, key=score, reverse=True)
    picked: list[str] = []
    for sentence in ranked:
        if len(" ".join(picked)) + len(sentence) > 700:
            break
        picked.append(sentence)
        if len(picked) >= limit:
            break
    return picked


def _company_phrase(passage: RetrievedPassage) -> str:
    bits = [passage.company_name or passage.ticker, passage.form]
    if passage.fiscal_year is not None:
        bits.append(f"FY{passage.fiscal_year}")
    return " · ".join(bits)


def run_demo_agent(query: str, deps: DocumentAgentDeps) -> GroundedAnswer:
    emit_agent_start(deps, model="demo-extractive")
    time.sleep(0.35)

    filters = _filters_from_query(query)
    deps.emit_status("searching", "Searching SEC filings…")
    passages = _search_sync(
        deps,
        query,
        ticker=filters.ticker,
        form=filters.form,
        fiscal_years=filters.fiscal_years,
    )
    deps.registry.register_many(passages)

    if not passages:
        emit_agent_done(deps)
        return GroundedAnswer(
            answer=INSUFFICIENT_EVIDENCE_ANSWER,
            citations=[],
            insufficient_evidence=True,
        )

    time.sleep(0.4)
    deps.emit_status("reading", "Reading source passages…")

    query_tokens = _content_tokens(query)
    selected = _select_passages(passages, query_tokens)
    weights = _token_weights(passages, query_tokens)

    evidence: list[str] = []
    citations: list[Citation] = []

    def collect(min_weight: float) -> None:
        for passage in selected:
            sentences = _best_sentences(passage, query_tokens, weights, limit=2, min_weight=min_weight)
            if not sentences:
                continue
            excerpt = " ".join(sentences)
            # Excerpts must be verbatim substrings of the chunk for grounding.
            normalized = re.sub(r"\s+", " ", passage.text)
            if excerpt not in normalized:
                start = normalized.find(sentences[0])
                excerpt = sentences[0] if start != -1 else normalized[: len(sentences[0]) + 100]
            index = len(citations) + 1
            evidence.append(f'> "{excerpt}" [{index}]')
            citations.append(
                Citation(
                    citation_index=index,
                    chunk_id=passage.chunk_id,
                    excerpt=excerpt,
                )
            )

    collect(min_weight=1.0)
    if not citations:
        collect(min_weight=0.0)

    emit_agent_done(deps)

    if not citations:
        return GroundedAnswer(
            answer=INSUFFICIENT_EVIDENCE_ANSWER,
            citations=[],
            insufficient_evidence=True,
        )

    sources = ", ".join(_company_phrase(p) for p in selected[: len(citations)])
    answer = (
        f"Here is what the retrieved filings say (demo mode — extractive answer from {sources}):\n\n"
        + "\n\n".join(evidence)
        + "\n\nOpen a citation to inspect the full passage and its surrounding context."
    )
    return GroundedAnswer(answer=answer, citations=citations)
