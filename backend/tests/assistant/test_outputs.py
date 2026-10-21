from app.assistant.outputs import Citation, GroundedAnswer


def test_grounded_answer_defaults():
    answer = GroundedAnswer(answer="text")
    assert answer.citations == []
    assert answer.insufficient_evidence is False


def test_citation_fields_required():
    citation = Citation(citation_index=1, chunk_id="00000000-0000-0000-0000-000000000000", excerpt="quote")
    assert citation.citation_index == 1
