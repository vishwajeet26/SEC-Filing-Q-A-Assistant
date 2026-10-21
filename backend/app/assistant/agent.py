"""Document agent: PydanticAI in real mode, extractive agent in demo mode."""

from __future__ import annotations

from pathlib import Path

from app.assistant.deps import DocumentAgentDeps
from app.assistant.outputs import GroundedAnswer
from app.assistant.status import emit_agent_done, emit_agent_start
from app.config import settings

_INSTRUCTIONS_PATH = Path(__file__).with_name("instructions.md")
INSTRUCTIONS = _INSTRUCTIONS_PATH.read_text(encoding="utf-8")

_document_agent = None


def get_document_agent():
    global _document_agent
    if _document_agent is None:
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider

        from app.assistant.tools import (
            read_chunk,
            read_chunks,
            read_surrounding_chunks,
            search_filings,
        )

        model = OpenAIChatModel(
            settings.openai_chat_model,
            provider=OpenAIProvider(api_key=settings.openai_api_key),
        )
        _document_agent = Agent(
            model,
            deps_type=DocumentAgentDeps,
            output_type=GroundedAnswer,
            instructions=INSTRUCTIONS,
            tools=[search_filings, read_chunks, read_chunk, read_surrounding_chunks],
        )
    return _document_agent


def _run_pydantic_agent(query: str, deps: DocumentAgentDeps) -> GroundedAnswer:
    from pydantic_ai import UsageLimits

    emit_agent_start(deps, model=settings.openai_chat_model)
    result = get_document_agent().run_sync(
        query,
        deps=deps,
        usage_limits=UsageLimits(request_limit=settings.openai_agent_request_limit),
    )
    emit_agent_done(deps)
    return result.output


def run_document_agent(query: str, deps: DocumentAgentDeps) -> GroundedAnswer:
    if settings.is_demo:
        from app.assistant.demo_agent import run_demo_agent

        return run_demo_agent(query, deps)
    return _run_pydantic_agent(query, deps)
