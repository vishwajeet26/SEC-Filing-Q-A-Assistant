"""Chat thread and message persistence."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, select

from app.auth.dependencies import CurrentUser
from app.chat.messages import (
    DEFAULT_THREAD_TITLE,
    row_to_ui_message,
    title_from_user_message,
    ui_message_to_insert,
)
from app.database.models import ChatMessage, ChatThread, MessageCitation
from app.database.session import get_session
from app.schemas.chat import CitationPart, ThreadResponse, UIMessage


@dataclass(frozen=True, slots=True)
class ThreadRow:
    id: uuid.UUID
    user_id: uuid.UUID
    title: str


def require_thread_access(thread_id: uuid.UUID, user: CurrentUser) -> ThreadRow:
    with get_session() as session:
        thread = session.scalar(select(ChatThread).where(ChatThread.id == thread_id))
        if thread is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

        if thread.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return ThreadRow(id=thread.id, user_id=thread.user_id, title=thread.title)


def list_threads(user: CurrentUser) -> list[ThreadResponse]:
    with get_session() as session:
        threads = session.scalars(
            select(ChatThread)
            .where(ChatThread.user_id == user.id)
            .order_by(ChatThread.updated_at.desc())
        ).all()
        return [
            ThreadResponse(
                id=thread.id,
                title=thread.title,
                created_at=thread.created_at,
                updated_at=thread.updated_at,
            )
            for thread in threads
        ]


def create_thread(user: CurrentUser, *, title: str | None = None) -> ThreadResponse:
    with get_session() as session:
        thread = ChatThread(user_id=user.id, title=title or DEFAULT_THREAD_TITLE)
        session.add(thread)
        session.commit()
        session.refresh(thread)
        return ThreadResponse(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
        )


def delete_thread(thread_id: uuid.UUID) -> None:
    with get_session() as session:
        session.execute(delete(ChatThread).where(ChatThread.id == thread_id))
        session.commit()


def load_messages(thread_id: uuid.UUID) -> list[UIMessage]:
    with get_session() as session:
        rows = session.scalars(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.sequence)
        ).all()
        messages = [row_to_ui_message(row) for row in rows]

        assistant_ids = [row.id for row in rows if row.role.value == "assistant"]
        if not assistant_ids:
            return messages

        citation_rows = session.scalars(
            select(MessageCitation)
            .where(MessageCitation.message_id.in_(assistant_ids))
            .order_by(MessageCitation.citation_index)
        ).all()

        citations_by_message: dict[str, list[MessageCitation]] = {}
        for row in citation_rows:
            citations_by_message.setdefault(str(row.message_id), []).append(row)

        hydrated: list[UIMessage] = []
        for row, message in zip(rows, messages, strict=True):
            if row.role.value != "assistant":
                hydrated.append(message)
                continue

            existing_chunk_ids = {
                part.data.chunk_id for part in message.parts if isinstance(part, CitationPart)
            }
            parts = list(message.parts)
            for citation in citations_by_message.get(str(row.id), []):
                if citation.chunk_id in existing_chunk_ids:
                    continue
                parts.append(
                    CitationPart(
                        id=str(citation.chunk_id),
                        data={
                            "citationIndex": citation.citation_index,
                            "chunkId": citation.chunk_id,
                            "excerpt": citation.excerpt,
                            "ticker": citation.ticker,
                            "companyName": citation.company_name,
                            "form": citation.form,
                            "filingDate": citation.filing_date,
                            "page": citation.page,
                            "section": citation.section,
                        },
                    )
                )
            hydrated.append(UIMessage(id=message.id, role=message.role, parts=parts))

        return hydrated


def _citation_rows_from_message(assistant_message: UIMessage) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if assistant_message.id is None:
        return rows

    for part in assistant_message.parts:
        if not isinstance(part, CitationPart):
            continue
        data = part.data
        rows.append(
            {
                "id": uuid.uuid4(),
                "message_id": uuid.UUID(assistant_message.id),
                "chunk_id": data.chunk_id,
                "citation_index": data.citation_index,
                "excerpt": data.excerpt,
                "ticker": data.ticker,
                "company_name": data.company_name,
                "form": data.form,
                "filing_date": data.filing_date,
                "page": data.page,
                "section": data.section,
            }
        )
    return rows


def append_grounded_turn(
    *,
    thread_id: uuid.UUID,
    user_message: UIMessage,
    assistant_message: UIMessage,
    thread_title: str,
) -> None:
    with get_session() as session:
        last_sequence = session.scalar(
            select(ChatMessage.sequence)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.sequence.desc())
            .limit(1)
        )
        next_sequence = (last_sequence or -1) + 1

        user_row = ChatMessage(
            **ui_message_to_insert(user_message, thread_id=thread_id, sequence=next_sequence)
        )
        assistant_row = ChatMessage(
            **ui_message_to_insert(
                assistant_message,
                thread_id=thread_id,
                sequence=next_sequence + 1,
            )
        )
        # Attach through the relationship so the unit of work flushes
        # messages before citations (FK on message_id).
        assistant_row.citations = [
            MessageCitation(**citation)
            for citation in _citation_rows_from_message(assistant_message)
        ]
        session.add_all([user_row, assistant_row])

        thread = session.scalar(select(ChatThread).where(ChatThread.id == thread_id))
        if thread is not None:
            thread.updated_at = datetime.now(UTC)
            if thread_title == DEFAULT_THREAD_TITLE:
                thread.title = title_from_user_message(user_message)

        session.commit()
