import pytest
from datetime import datetime, timezone
from scripts.models import (
    Issue, Document, Decision, Commitment,
    Entity, Note, Relation, SyncRun,
)


def _now():
    return datetime.now(timezone.utc).isoformat()


class TestIssue:
    def test_valid_issue(self):
        issue = Issue(
            id="tracker:PM-123",
            source="tracker",
            source_ref="PM-123",
            key="PM-123",
            summary="Fix login bug",
            status="open",
            assignee="vladk",
            queue="PM",
            dedupe_key="tracker:PM-123",
            fetched_at=_now(),
        )
        assert issue.kind == "issue"
        assert issue.confidence == "canonical"

    def test_issue_key_pattern(self):
        with pytest.raises(ValueError):
            Issue(
                id="tracker:bad",
                source="tracker",
                source_ref="bad",
                key="lowercase-123",
                summary="test",
                status="open",
                dedupe_key="tracker:bad",
                fetched_at=_now(),
            )

    def test_issue_empty_summary_rejected(self):
        with pytest.raises(ValueError):
            Issue(
                id="tracker:PM-1",
                source="tracker",
                source_ref="PM-1",
                key="PM-1",
                summary="",
                status="open",
                dedupe_key="tracker:PM-1",
                fetched_at=_now(),
            )


class TestDocument:
    def test_valid_document(self):
        doc = Document(
            id="intrasearch:abc123",
            source="intrasearch",
            source_ref="abc123",
            title="Onboarding Guide",
            url="https://wiki.yandex-team.ru/onboarding",
            dedupe_key="intrasearch:abc123",
            fetched_at=_now(),
        )
        assert doc.kind == "document"

    def test_document_requires_title(self):
        with pytest.raises(ValueError):
            Document(
                id="intrasearch:x",
                source="intrasearch",
                source_ref="x",
                title="",
                url="https://example.com",
                dedupe_key="intrasearch:x",
                fetched_at=_now(),
            )


class TestDecision:
    def test_valid_decision(self):
        d = Decision(
            id="manual:d1",
            source="manual",
            source_ref="user-input",
            summary="We decided to use JSONL for the ledger",
            dedupe_key="manual:d1",
            fetched_at=_now(),
        )
        assert d.kind == "decision"


class TestCommitment:
    def test_valid_commitment(self):
        c = Commitment(
            id="tracker:PM-99",
            source="tracker",
            source_ref="PM-99",
            summary="Ship auth refactor by Q2",
            owner="vladk",
            due_date="2026-06-30",
            dedupe_key="tracker:PM-99",
            fetched_at=_now(),
        )
        assert c.status == "active"

    def test_commitment_status_values(self):
        c = Commitment(
            id="x:1",
            source="manual",
            source_ref="x",
            summary="test",
            status="fulfilled",
            dedupe_key="x:1",
            fetched_at=_now(),
        )
        assert c.status == "fulfilled"


class TestEntity:
    def test_valid_entity(self):
        e = Entity(
            id="person:vladk",
            kind="person",
            name="Vlad Kiaune",
            dedupe_key="person:vladk",
        )
        assert e.aliases == []


class TestNote:
    def test_valid_note(self):
        n = Note(
            id="manual:n1",
            source="manual",
            text="Remember to check the deploy logs",
            dedupe_key="manual:n1",
            fetched_at=_now(),
        )
        assert n.kind == "note"


class TestRelation:
    def test_valid_relation(self):
        r = Relation(
            id="rel:1",
            source="tracker",
            from_ref="project:lumi",
            to_ref="tracker:PM-123",
            relation_type="belongs_to",
            dedupe_key="rel:project:lumi->tracker:PM-123:belongs_to",
            fetched_at=_now(),
        )
        assert r.kind == "relation"


class TestSyncRun:
    def test_valid_sync_run(self):
        s = SyncRun(
            id="sync:abc",
            recipe="my_work",
            started_at=_now(),
            status="running",
        )
        assert s.kind == "sync_run"
        assert s.raw_records_count == 0
