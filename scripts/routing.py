"""Schema-driven record routing.

The model NEVER chooses a destination file freely (PRD §5.8).
Routing is deterministic based on record kind.
"""
from __future__ import annotations

from scripts.models import LEDGER_FILES


class RoutingError(Exception):
    pass


def route_record(kind: str) -> str:
    """Return the ledger filename for a given record kind."""
    filename = LEDGER_FILES.get(kind)
    if filename is None:
        raise RoutingError(
            f"Unknown record kind: {kind!r}. "
            f"Valid kinds: {sorted(LEDGER_FILES.keys())}"
        )
    return filename
