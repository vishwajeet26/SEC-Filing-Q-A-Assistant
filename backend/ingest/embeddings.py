"""Text embeddings: OpenAI in real mode, deterministic hashed vectors in demo mode."""

from __future__ import annotations

import hashlib
import math
import re

from app.config import settings

_PROBES = 4  # hash probes per token


def _hash_embed(text: str, dimensions: int) -> list[float]:
    """Deterministic bag-of-words (+ bigram) hashing embedding.

    Not semantically smart — it approximates lexical overlap via cosine
    similarity, which combined with full-text search and RRF gives the demo
    usable hybrid retrieval without an API key.
    """
    vector = [0.0] * dimensions
    tokens = [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 1]
    grams = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
    for gram in grams:
        raw = gram.encode("utf-8")
        for probe in range(_PROBES):
            digest = hashlib.blake2b(raw, digest_size=8, person=bytes([probe])).digest()
            value = int.from_bytes(digest, "big")
            index = value % dimensions
            sign = -1.0 if (value >> 63) & 1 else 1.0
            vector[index] += sign
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def _openai_embed(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    out: list[list[float]] = []
    batch_size = 128
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.embeddings.create(
            input=batch,
            model=settings.openai_embedding_model,
            dimensions=settings.openai_embedding_dimensions,
        )
        for item in response.data:
            embedding = item.embedding
            if len(embedding) != settings.openai_embedding_dimensions:
                raise ValueError(
                    f"Expected embedding dimension {settings.openai_embedding_dimensions}, "
                    f"got {len(embedding)}"
                )
            out.append(embedding)
    return out


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if settings.is_demo:
        return [_hash_embed(text, settings.openai_embedding_dimensions) for text in texts]
    return _openai_embed(texts)
