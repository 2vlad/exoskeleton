"""End-to-end integration tests for the sync pipeline.

Tests the full flow: fixture data → normalize → merge → quality check → rebuild views.
"""
import json
import pytest
from pathlib import Path
from scripts.normalize import normalize_tracker_issues, normalize_intrasearch_hits
from scripts.merge_ledger import merge_records, read_jsonl, write_jsonl
from scripts.sync_quality import run_quality_checks
from scripts.rebuild_views import rebuild_active_view, rebuild_all_views


class TestFullSyncPipeline:
    def test_tracker_issues_pipeline(self, brain_dir, tracker_fixtures):
        """Full pipeline: raw tracker → normalize → merge → quality → views."""
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        assert len(issues) == 3

        records = [i.model_dump() for i in issues]
        stats = merge_records(brain_dir / "ledger" / "issues.jsonl", records)
        assert stats["inserted"] == 3

        report = run_quality_checks(brain_dir)
        assert report.passed

        active_md = rebuild_active_view(brain_dir)
        assert "PM-123" in active_md
        assert "PM-456" in active_md
        assert "LUMI-78" in active_md

    def test_idempotent_sync(self, brain_dir, tracker_fixtures):
        """Running sync twice produces identical results."""
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        records = [i.model_dump() for i in issues]

        merge_records(brain_dir / "ledger" / "issues.jsonl", records)
        merge_records(brain_dir / "ledger" / "issues.jsonl", records)

        ledger = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
        assert len(ledger) == 3

    def test_empty_sync_preserves_state(self, brain_dir, tracker_fixtures):
        """Empty sync result must NOT delete existing issues."""
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        records = [i.model_dump() for i in issues]
        merge_records(brain_dir / "ledger" / "issues.jsonl", records)

        stats = merge_records(brain_dir / "ledger" / "issues.jsonl", [])
        assert stats["inserted"] == 0
        assert stats["updated"] == 0

        ledger = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
        assert len(ledger) == 3

    def test_broken_response_quarantined(self, brain_dir, broken_fixtures):
        """Malformed issues are skipped, valid ones are kept."""
        issues = normalize_tracker_issues(broken_fixtures["partial_list"])
        assert len(issues) == 1
        assert issues[0].key == "PM-123"

    def test_mixed_source_pipeline(self, brain_dir, tracker_fixtures, intrasearch_fixtures):
        """Issues from tracker + docs from intrasearch coexist in ledger."""
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [i.model_dump() for i in issues],
        )

        docs = normalize_intrasearch_hits(
            intrasearch_fixtures["doc_results"],
            query="onboarding",
        )
        merge_records(
            brain_dir / "ledger" / "docs.jsonl",
            [d.model_dump() for d in docs],
        )

        assert len(read_jsonl(brain_dir / "ledger" / "issues.jsonl")) == 3
        assert len(read_jsonl(brain_dir / "ledger" / "docs.jsonl")) == 2

        report = run_quality_checks(brain_dir)
        assert report.passed

        results = rebuild_all_views(brain_dir)
        assert results["active"] > 0
