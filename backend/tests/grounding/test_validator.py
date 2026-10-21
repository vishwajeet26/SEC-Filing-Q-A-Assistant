import uuid

from app.assistant.deps import TurnRegistry
from app.assistant.outputs import Citation, GroundedAnswer
from app.grounding.validator import (
    GroundingValidator,
    prune_unreferenced_citations,
)
from app.retrieval.types import RetrievedPassage
from datetime import date


def _passage(chunk_id: uuid.UUID, text: str) -> RetrievedPassage:
    return RetrievedPassage(
        chunk_id=chunk_id,
        document_id=uuid.uuid4(),
        chunk_index=0,
        text=text,
        page=None,
        section=None,
        fusion_score=0.5,
        ticker="AAPL",
        company_name="Apple Inc.",
        form="10-K",
        filing_date=date(2025, 11, 1),
    )


def _registry(*passages: RetrievedPassage) -> TurnRegistry:
    registry = TurnRegistry()
    registry.register_many(list(passages))
    return registry


def test_valid_answer_passes():
    chunk = uuid.uuid4()
    passage = _passage(chunk, "iPhone revenue grew 7 percent in fiscal 2025.")
    answer = GroundedAnswer(
        answer="iPhone revenue grew [1].",
        citations=[Citation(citation_index=1, chunk_id=chunk, excerpt="iPhone revenue grew 7 percent")],
    )
    result = GroundingValidator().validate_sync(answer, _registry(passage))
    assert result.ok


def test_unretrieved_chunk_fails():
    answer = GroundedAnswer(
        answer="Something [1].",
        citations=[Citation(citation_index=1, chunk_id=uuid.uuid4(), excerpt="Something")],
    )
    result = GroundingValidator().validate_sync(answer, _registry())
    assert not result.ok
    assert "retrieved" in result.error


def test_noncontiguous_indices_fail():
    chunk_a, chunk_b = uuid.uuid4(), uuid.uuid4()
    passages = [_passage(chunk_a, "text text text"), _passage(chunk_b, "more text")]
    answer = GroundedAnswer(
        answer="A [1] b [3].",
        citations=[
            Citation(citation_index=1, chunk_id=chunk_a, excerpt="text"),
            Citation(citation_index=3, chunk_id=chunk_b, excerpt="more"),
        ],
    )
    result = GroundingValidator().validate_sync(answer, passages and _registry(*passages))
    assert not result.ok
    assert "contiguous" in result.error


def test_nonverbatim_excerpt_fails_substring_judge():
    chunk = uuid.uuid4()
    passage = _passage(chunk, "AWS operating income increased year over year.")
    answer = GroundedAnswer(
        answer="AWS grew [1].",
        citations=[Citation(citation_index=1, chunk_id=chunk, excerpt="AWS revenue doubled in 2030")],
    )
    result = GroundingValidator().validate_sync(answer, _registry(passage))
    assert not result.ok


def test_insufficient_evidence_must_not_cite():
    chunk = uuid.uuid4()
    answer = GroundedAnswer(
        answer="No evidence.",
        citations=[Citation(citation_index=1, chunk_id=chunk, excerpt="x")],
        insufficient_evidence=True,
    )
    result = GroundingValidator().validate_sync(answer, _registry())
    assert not result.ok


def test_prune_unreferenced_citations():
    chunk = uuid.uuid4()
    answer = GroundedAnswer(
        answer="Only one marker [1].",
        citations=[
            Citation(citation_index=1, chunk_id=chunk, excerpt="a"),
            Citation(citation_index=2, chunk_id=uuid.uuid4(), excerpt="b"),
        ],
    )
    pruned = prune_unreferenced_citations(answer)
    assert [c.citation_index for c in pruned.citations] == [1]
