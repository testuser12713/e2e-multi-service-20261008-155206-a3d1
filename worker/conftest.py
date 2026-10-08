"""Ensure the repository root is importable when pytest runs from worker/.

The pipeline runs ``PYTHONPATH=. py -m pytest`` from inside ``worker/``; adding
the parent directory lets tests import the ``worker`` package exactly the way
``python -m worker.main`` does at runtime.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
