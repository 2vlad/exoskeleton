import json
import pytest
from pathlib import Path
from scripts.sync_quality import run_quality_checks, QualityReport
from scripts.merge_ledger import write_jsonl


@pytest.fixture
def brain_dir(tmp_path):
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    state = tmp_path / "state"
    state.mkdir()
    return tmp_path


class TestQualityChecks:
    def test_no_duplicate_dedupe_keys(self, brain_dir):
        issues = [
            {"id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A", "source": "tracker"},
            {"id": "tracker:PM-2", "dedupe_key": "tracker:PM-2", "key": "PM-2", "summary": "B", "source": "tracker"},
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert report.passed
        assert len(report.warnings) == 0

    def test_duplicate_dedupe_keys_warned(self, brain_dir):
        issues = [
            {"id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A", "source": "tracker"},
            {"id": "tracker:PM-1-dup", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A dup", "source": "tracker"},
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert not report.passed
        assert any("duplicate" in w.lower() for w in report.warnings)

    def test_missing_provenance_warned(self, brain_dir):
        issues = [
            {"id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A"},
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert any("provenance" in w.lower() or "source" in w.lower() for w in report.warnings)

    def test_unresolved_entities_counted(self, brain_dir):
        issues = [
            {
                "id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1",
                "summary": "A", "source": "tracker",
                "entity_refs": ["unresolved:some person"],
            },
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert report.unresolved_entities_count == 1

    def test_empty_ledger_passes(self, brain_dir):
        (brain_dir / "ledger" / "issues.jsonl").write_text("")
        report = run_quality_checks(brain_dir)
        assert report.passed
