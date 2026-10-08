"""Text analysis computations.

Implements the three analyses a job can request: ``word_count``, ``top_words``
and ``reading_time``. The result shapes match the shared contract:

- ``word_count``     -> ``{"word_count": int}``
- ``top_words``      -> ``{"top_words": [{"word": str, "count": int}, ...]}``
- ``reading_time``   -> ``{"reading_time_minutes": float, "word_count": int}``

An unknown analysis raises ``ValueError``; the job runner records that message
and marks the job ``failed``.
"""

from __future__ import annotations

import string

_PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)


def word_count(text: str) -> int:
    """Number of words: whitespace split after stripping the text."""
    return len(text.strip().split())


def reading_time(text: str) -> float:
    """Reading time in minutes at 200 words per minute, rounded to one decimal."""
    return round(word_count(text) / 200, 1)


def top_words(text: str, limit: int = 10) -> list[dict]:
    """Most frequent words: lowercased, punctuation stripped, ties alphabetical.

    At most ``limit`` entries are returned. Ties in count are ordered
    alphabetically so the result is deterministic.
    """
    cleaned = text.lower().translate(_PUNCTUATION_TABLE)
    counts: dict[str, int] = {}
    for word in cleaned.split():
        counts[word] = counts.get(word, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"word": word, "count": count} for word, count in ordered[:limit]]


def compute(analysis: str, text: str) -> dict:
    """Compute the result for ``analysis`` over ``text``.

    Raises ``ValueError`` for an analysis outside the three allowed values.
    """
    if analysis == "word_count":
        return {"word_count": word_count(text)}
    if analysis == "top_words":
        return {"top_words": top_words(text)}
    if analysis == "reading_time":
        return {"reading_time_minutes": reading_time(text), "word_count": word_count(text)}
    raise ValueError(f"unknown analysis: {analysis!r}")
