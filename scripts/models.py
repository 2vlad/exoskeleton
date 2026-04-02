"""Pydantic models for all ledger record types.

These models enforce the schemas defined in brain/system/schemas/.
Every record written to the ledger MUST pass through these models.
"""
from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


_ISSUE_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


class _LedgerBase(BaseModel):
    """Common fields for all ledger records with provenance."""
    id: str
    source: str
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    entity_refs: list[str] = Field(default_factory=list)
    dedupe_key: str
    confidence: str = "canonical"
    fetched_at: str
    observed_at: Optional[str] = None
    payload: dict = Field(default_factory=dict)


class Issue(_LedgerBase):
    kind: str = "issue"
    key: str
    summary: str
    status: str
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    queue: Optional[str] = None
    priority: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None

    @field_validator("key")
    @classmethod
    def _validate_key(cls, v: str) -> str:
        if not _ISSUE_KEY_RE.match(v):
            raise ValueError(f"Invalid issue key format: {v!r}")
        return v

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("summary must not be empty")
        return v


class Document(_LedgerBase):
    kind: str = "document"
    title: str
    url: str
    snippet: Optional[str] = None
    query: Optional[str] = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v


class Decision(_LedgerBase):
    kind: str = "decision"
    summary: str
    context: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("summary must not be empty")
        return v


class Commitment(_LedgerBase):
    kind: str = "commitment"
    summary: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "active"

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("summary must not be empty")
        return v

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        allowed = {"active", "fulfilled", "stale", "cancelled"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class Entity(BaseModel):
    id: str
    kind: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    external_ids: dict = Field(default_factory=dict)
    dedupe_key: str
    payload: dict = Field(default_factory=dict)

    @field_validator("kind")
    @classmethod
    def _validate_kind(cls, v: str) -> str:
        allowed = {"person", "project", "team", "goal", "system", "queue", "document"}
        if v not in allowed:
            raise ValueError(f"kind must be one of {allowed}")
        return v


class Note(BaseModel):
    id: str
    source: str
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    kind: str = "note"
    text: str
    entity_refs: list[str] = Field(default_factory=list)
    dedupe_key: str
    confidence: str = "canonical"
    fetched_at: str
    payload: dict = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def _validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        return v


class Relation(BaseModel):
    id: str
    source: str
    kind: str = "relation"
    from_ref: str
    to_ref: str
    relation_type: str
    dedupe_key: str
    fetched_at: str
    payload: dict = Field(default_factory=dict)

    @field_validator("relation_type")
    @classmethod
    def _validate_relation_type(cls, v: str) -> str:
        allowed = {"belongs_to", "assigned_to", "authored_by", "related_to", "depends_on", "mentions"}
        if v not in allowed:
            raise ValueError(f"relation_type must be one of {allowed}")
        return v


class SyncRun(BaseModel):
    id: str
    kind: str = "sync_run"
    recipe: str
    command: Optional[str] = None
    sources_touched: list[str] = Field(default_factory=list)
    raw_records_count: int = 0
    normalized_records_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    unresolved_entities_count: int = 0
    publish_status: str = "running"
    degraded_sources: list[str] = Field(default_factory=list)
    started_at: str
    finished_at: Optional[str] = None
    latency_ms: Optional[int] = None
    status: str = "running"

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        allowed = {"running", "success", "partial", "failed"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


RECORD_MODELS = {
    "issue": Issue,
    "document": Document,
    "decision": Decision,
    "commitment": Commitment,
    "entity": Entity,
    "note": Note,
    "relation": Relation,
    "sync_run": SyncRun,
}

LEDGER_FILES = {
    "issue": "issues.jsonl",
    "document": "docs.jsonl",
    "decision": "decisions.jsonl",
    "commitment": "commitments.jsonl",
    "entity": "entities.jsonl",
    "note": "notes.jsonl",
    "relation": "relations.jsonl",
    "sync_run": "sync_runs.jsonl",
}
