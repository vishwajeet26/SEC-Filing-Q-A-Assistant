"""Pydantic models for chat API request and response bodies."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TextPart(BaseModel):
    type: Literal["text"] = "text"
    text: str


class CitationPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    citation_index: int = Field(alias="citationIndex")
    chunk_id: uuid.UUID = Field(alias="chunkId")
    excerpt: str
    ticker: str
    company_name: str | None = Field(default=None, alias="companyName")
    form: str
    filing_date: date = Field(alias="filingDate")
    page: str | None = None
    section: str | None = None


class CitationPart(BaseModel):
    type: Literal["data-citation"] = "data-citation"
    id: str | None = None
    data: CitationPayload


class CitationContextChunk(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chunk_id: uuid.UUID = Field(alias="chunkId")
    chunk_index: int = Field(alias="chunkIndex")
    role: Literal["previous", "anchor", "next"]
    text: str
    page: str | None = None
    section: str | None = None


class CitationContextTable(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    table_index: int = Field(alias="tableIndex")
    title: str | None = None
    units: str | None = None
    markdown: str
    table_data: dict[str, Any] = Field(alias="tableData")


class CitationContextResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    anchor_chunk_id: uuid.UUID = Field(alias="anchorChunkId")
    document_id: uuid.UUID = Field(alias="documentId")
    ticker: str
    company_name: str | None = Field(default=None, alias="companyName")
    form: str
    filing_date: date = Field(alias="filingDate")
    source_url: str | None = Field(default=None, alias="sourceUrl")
    chunks: list[CitationContextChunk]
    table: CitationContextTable | None = None


class StatusPayload(BaseModel):
    stage: str
    message: str


class StatusPart(BaseModel):
    type: Literal["data-status"] = "data-status"
    id: str | None = None
    data: StatusPayload


MessagePart = Annotated[TextPart | CitationPart | StatusPart, Field(discriminator="type")]


class UIMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    role: Literal["user", "assistant", "system"]
    parts: list[MessagePart]

    @model_validator(mode="before")
    @classmethod
    def _drop_unknown_parts(cls, data: Any) -> Any:
        """Client history can carry part types we don't model (e.g. transient
        data parts from earlier turns). Drop them instead of failing."""
        if isinstance(data, dict) and isinstance(data.get("parts"), list):
            known = {"text", "data-citation", "data-status"}
            data = {
                **data,
                "parts": [
                    p
                    for p in data["parts"]
                    if not isinstance(p, dict) or p.get("type") in known
                ],
            }
        return data


class CreateThreadRequest(BaseModel):
    title: str | None = None


class ThreadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    title: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ThreadListResponse(BaseModel):
    threads: list[ThreadResponse]


class MessageHistoryResponse(BaseModel):
    messages: list[UIMessage]


class StreamRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    thread_id: uuid.UUID = Field(validation_alias="threadId")
    messages: list[UIMessage]


class DemoSignInRequest(BaseModel):
    email: str
    password: str


class DemoSessionResponse(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    user: dict[str, str]
