"""Map internal agent/tool events to analyst-friendly pipeline status."""

from __future__ import annotations

from app.assistant.deps import DocumentAgentDeps


def emit_tool_start(deps: DocumentAgentDeps, name: str, detail: str) -> None:
    stage, message = _tool_start_status(name, detail)
    deps.emit_status(stage, message)


def emit_agent_start(deps: DocumentAgentDeps, *, model: str) -> None:
    # The orchestrator already streams "analyzing" before the agent task starts;
    # this hook exists for smoke scripts, so it stays silent in the SSE path.
    return


def emit_agent_done(deps: DocumentAgentDeps) -> None:
    # Same: the orchestrator streams "verifying" once the agent task completes.
    return


def _tool_start_status(name: str, detail: str) -> tuple[str, str]:
    if name == "search_filings":
        suffix = f" ({detail})" if detail != "no filters" else ""
        return "searching", f"Searching SEC filings…{suffix}"
    if name == "read_surrounding_chunks":
        return "reading", "Reading surrounding context…"
    if name in {"read_chunk", "read_chunks"}:
        return "reading", "Reading source passages…"
    return "reading", "Reading source documents…"
