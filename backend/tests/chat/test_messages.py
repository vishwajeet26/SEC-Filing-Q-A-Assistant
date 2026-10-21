import uuid

from app.chat.messages import (
    build_assistant_message,
    row_to_ui_message,
    text_from_parts,
    title_from_user_message,
)
from app.assistant.outputs import Citation, GroundedAnswer
from app.schemas.chat import TextPart, UIMessage


def test_text_from_parts_ignores_non_text():
    message = UIMessage(id="1", role="user", parts=[TextPart(text="hello "), TextPart(text="world")])
    assert text_from_parts(message.parts) == "hello world"


def test_row_to_ui_message_falls_back_to_content():
    row = {"id": str(uuid.uuid4()), "role": "user", "content": "fallback", "parts": []}
    message = row_to_ui_message(row)
    assert message.parts[0].type == "text"
    assert message.parts[0].text == "fallback"


def test_row_to_ui_message_parses_parts():
    row = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": None,
        "parts": [{"type": "text", "text": "answer"}],
    }
    message = row_to_ui_message(row)
    assert text_from_parts(message.parts) == "answer"


def test_title_from_user_message_truncates():
    text = "x" * 400
    message = UIMessage(id="1", role="user", parts=[TextPart(text=text)])
    title = title_from_user_message(message)
    assert len(title) == 255
    assert title.endswith("...")


def test_build_assistant_message_includes_citation_parts():
    chunk_id = uuid.uuid4()
    answer = GroundedAnswer(
        answer="Quoted [1].",
        citations=[Citation(citation_index=1, chunk_id=chunk_id, excerpt="Quoted")],
    )

    class FakeRegistry:
        passages_by_chunk_id = {
            chunk_id: type(
                "P",
                (),
                {
                    "ticker": "MSFT",
                    "company_name": "Microsoft",
                    "form": "10-K",
                    "filing_date": "2025-07-30",
                    "page": None,
                    "section": "Item 7",
                },
            )()
        }

    message = build_assistant_message(answer, FakeRegistry())
    assert message.role == "assistant"
    citation_parts = [p for p in message.parts if p.type == "data-citation"]
    assert len(citation_parts) == 1
    assert citation_parts[0].data.ticker == "MSFT"
