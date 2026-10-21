"""Run one question through the agent + grounding validator. Usage:

uv run python -m scripts.smoke_assistant "How does Apple describe Services growth?"
"""

from __future__ import annotations

import argparse
import uuid

from app.assistant.agent import run_document_agent
from app.assistant.deps import DocumentAgentDeps, TurnRegistry
from app.assistant.progress import add_progress_listener
from app.grounding.validator import GroundingValidator
from app.retrieval.retriever import DocumentRetriever


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--ticker", default=None)
    args = parser.parse_args()

    add_progress_listener(lambda message: print(f"· {message}"))

    registry = TurnRegistry()
    deps = DocumentAgentDeps(
        retriever=DocumentRetriever(),
        registry=registry,
        thread_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        on_status=lambda stage, message: print(f"[{stage}] {message}"),
    )

    answer = run_document_agent(args.question, deps)
    validation = GroundingValidator().validate_sync(answer, registry)

    print("\n--- ANSWER ---")
    print(answer.answer)
    print("\n--- CITATIONS ---")
    for citation in answer.citations:
        print(f"[{citation.citation_index}] chunk {citation.chunk_id}")
        print(f"    {citation.excerpt[:200]}")
    print(f"\ninsufficient_evidence={answer.insufficient_evidence}")
    print(f"grounding={'OK' if validation.ok else f'FAILED: {validation.error}'}")


if __name__ == "__main__":
    main()
