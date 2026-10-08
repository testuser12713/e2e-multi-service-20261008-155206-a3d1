"""Job processing step.

The real claim-and-compute logic is delivered by the follow-up ticket; this
module only fixes the interface.
"""

from __future__ import annotations

import sqlite3


def process_one(conn: sqlite3.Connection) -> int | None:
    """Claim and process at most one pending job.

    Returns the id of the processed job, or ``None`` when there was nothing to
    do. Not implemented yet: the skeleton processes nothing.
    """
    return None
