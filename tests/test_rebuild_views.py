import json
import pytest
from pathlib import Path
from scripts.rebuild_views import (
    rebuild_active_view,
    rebuild_decisions_view,
    rebuild_commitments_view,
    rebuild_project_view,
)
from scripts.merge_ledger import write_jsonl


def _now():
    return "2026-04-02T12:00:00+00:00"


@pytest.fixture
def brain_dir(tmp_path):
    """Set up a minimal brain directory with ledger data."""
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    views = tmp_path / "views"
    views.mkdir()
    (views / "projects").mkdir()
    (views / "people").mkdir()
    control = tmp_path / "control"
    control.mkdir()

    (control / "role.md").write_text("# Role\n\nSenior PM at Practicum\n")
    (control / "week.md").write_text("# Week Focus\n\n- Ship onboarding v2\n- Review retention metrics\n")

    issues = [
        {
            "id": "tracker:PM-123", "kind": "issue", "key": "PM-123",
            "summary": "Implement onboarding flow", "status": "inProgress",
            "assignee": "vladk", "queue": "PM", "priority": "normal",
            "dedupe_key": "tracker:PM-123", "source": "tracker",
            "confidence": "canonical", "fetched_at": _now(),
            "updated_at": "2026-04-01T10:30:00+00:00",
        },
        {
            "id": "tracker:PM-456", "kind": "issue", "key": "PM-456",
            "summary": "Define retention metrics", "status": "open",
            "assignee": "vladk", "queue": "PM", "priority": "critical",
            "dedupe_key": "tracker:PM-456", "source": "tracker",
            "confidence": "canonical", "fetched_at": _now(),
            "updated_at": "2026-04-02T09:00:00+00:00",
        },
        {
            "id": "tracker:LUMI-78", "kind": "issue", "key": "LUMI-78",
            "summary": "Launch readiness review", "status": "open",
            "assignee": "vladk", "queue": "LUMI", "priority": "high",
            "dedupe_key": "tracker:LUMI-78", "source": "tracker",
            "confidence": "canonical", "fetched_at": _now(),
            "updated_at": "2026-03-30T16:00:00+00:00",
        },
    ]
    write_jsonl(ledger / "issues.jsonl", issues)

    decisions = [
        {
            "id": "manual:d1", "kind": "decision", "source": "manual",
            "source_ref": "sync-2026-04-01", "summary": "Switch to progressive disclosure for onboarding",
            "context": "Wizard flow had 40% drop-off at step 3",
            "decided_by": "vladk", "decided_at": "2026-04-01T10:00:00+00:00",
            "entity_refs": ["project:navi"], "dedupe_key": "manual:d1",
            "confidence": "canonical", "fetched_at": _now(),
        },
    ]
    write_jsonl(ledger / "decisions.jsonl", decisions)

    commitments = [
        {
            "id": "tracker:PM-99", "kind": "commitment", "source": "tracker",
            "source_ref": "PM-99", "summary": "Ship onboarding v2 by Q2 end",
            "owner": "vladk", "due_date": "2026-06-30", "status": "active",
            "entity_refs": [], "dedupe_key": "tracker:PM-99",
            "confidence": "canonical", "fetched_at": _now(),
        },
    ]
    write_jsonl(ledger / "commitments.jsonl", commitments)

    for name in ["docs.jsonl", "entities.jsonl", "notes.jsonl", "relations.jsonl", "sync_runs.jsonl"]:
        (ledger / name).write_text("")

    state = tmp_path / "state"
    state.mkdir()
    (state / "source_state.json").write_text(json.dumps({
        "last_sync": {"tracker": "2026-04-02T12:00:00+00:00"},
        "source_health": {"tracker": "ok"},
    }))

    return tmp_path


class TestRebuildActiveView:
    def test_generates_active_md(self, brain_dir):
        output = rebuild_active_view(brain_dir)
        assert "PM-123" in output
        assert "PM-456" in output
        assert "LUMI-78" in output
        assert "inProgress" in output or "In Progress" in output

    def test_includes_week_focus(self, brain_dir):
        output = rebuild_active_view(brain_dir)
        assert "onboarding" in output.lower()

    def test_includes_sync_freshness(self, brain_dir):
        output = rebuild_active_view(brain_dir)
        assert "tracker" in output.lower()


class TestRebuildDecisionsView:
    def test_generates_decisions_md(self, brain_dir):
        output = rebuild_decisions_view(brain_dir)
        assert "progressive disclosure" in output.lower()


class TestRebuildCommitmentsView:
    def test_generates_commitments_md(self, brain_dir):
        output = rebuild_commitments_view(brain_dir)
        assert "onboarding v2" in output.lower()
        assert "2026-06-30" in output


class TestRebuildProjectView:
    def test_generates_project_md(self, brain_dir):
        output = rebuild_project_view(brain_dir, project_id="navi", project_name="Navigator")
        assert "progressive disclosure" in output.lower()
