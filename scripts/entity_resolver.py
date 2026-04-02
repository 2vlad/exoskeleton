"""Deterministic entity resolution using aliases and identities.

Resolution order (per PRD §15.3):
1. Exact external IDs
2. Alias map (case-insensitive)
3. Normalized name match
4. Unresolved → review queue

The model is NOT involved in resolution. This is purely deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResolveResult:
    resolved_id: str | None
    confidence: str  # "exact", "alias", "unresolved"
    candidates: list[str]
    raw_text: str


class EntityResolver:
    def __init__(self, aliases: dict, identities: dict):
        self._lookup: dict[str, list[tuple[str, str]]] = {}
        self._build_lookup(aliases)
        self._identities = identities

    def _build_lookup(self, aliases: dict) -> None:
        kind_map = {
            "projects": "project",
            "people": "person",
            "queues": "queue",
        }
        for section, kind in kind_map.items():
            entries = aliases.get(section, {})
            if not isinstance(entries, dict):
                continue
            for canonical_id, alias_list in entries.items():
                self._add(canonical_id.lower(), kind, canonical_id)
                for alias in alias_list:
                    self._add(alias.lower(), kind, canonical_id)

    def _add(self, lowered: str, kind: str, canonical_id: str) -> None:
        key = lowered.strip()
        if key not in self._lookup:
            self._lookup[key] = []
        entry = (kind, canonical_id)
        if entry not in self._lookup[key]:
            self._lookup[key].append(entry)

    def resolve(self, raw_text: str, kind: str | None = None) -> ResolveResult:
        lowered = raw_text.strip().lower()

        if lowered in self._lookup:
            matches = self._lookup[lowered]
            if kind:
                matches = [(k, cid) for k, cid in matches if k == kind]
            if len(matches) == 1:
                k, cid = matches[0]
                conf = "exact" if lowered == cid.lower() else "alias"
                return ResolveResult(
                    resolved_id=f"{k}:{cid}",
                    confidence=conf,
                    candidates=[f"{k}:{cid}"],
                    raw_text=raw_text,
                )
            elif len(matches) > 1:
                return ResolveResult(
                    resolved_id=None,
                    confidence="unresolved",
                    candidates=[f"{k}:{cid}" for k, cid in matches],
                    raw_text=raw_text,
                )

        return ResolveResult(
            resolved_id=None,
            confidence="unresolved",
            candidates=[],
            raw_text=raw_text,
        )
