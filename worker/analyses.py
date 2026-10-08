"""Text analysis computations.

The real implementations of ``word_count``, ``top_words`` and ``reading_time``
are delivered by the follow-up ticket; this module only fixes the interface.
"""

from __future__ import annotations


def compute(analysis: str, text: str) -> dict:
    """Compute the result for ``analysis`` over ``text``.

    Not implemented yet.
    """
    raise NotImplementedError("compute() is implemented by the worker analyses ticket")
