import json
import pytest
from pathlib import Path
from scripts.merge_ledger import merge_records, read_jsonl, write_jsonl


@pytest.fixture
def tmp_ledger(tmp_path):
    ledger = tmp_path / "issues.jsonl"
    ledger.write_text("")
    return ledger


class TestMergeRecords:
    def test_insert_new_records(self, tmp_ledger):
        records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Issue A"},
            {"id": "tracker:PM-456", "dedupe_key": "tracker:PM-456", "summary": "Issue B"},
        ]
        stats = merge_records(tmp_ledger, records)
        assert stats["inserted"] == 2
        assert stats["updated"] == 0
        result = read_jsonl(tmp_ledger)
        assert len(result) == 2

    def test_upsert_existing_record(self, tmp_ledger):
        existing = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Old summary"},
        ]
        write_jsonl(tmp_ledger, existing)

        new_records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "New summary"},
        ]
        stats = merge_records(tmp_ledger, new_records)
        assert stats["inserted"] == 0
        assert stats["updated"] == 1
        result = read_jsonl(tmp_ledger)
        assert len(result) == 1
        assert result[0]["summary"] == "New summary"

    def test_idempotent_merge(self, tmp_ledger):
        records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Issue A"},
        ]
        merge_records(tmp_ledger, records)
        merge_records(tmp_ledger, records)
        result = read_jsonl(tmp_ledger)
        assert len(result) == 1

    def test_empty_new_records_preserves_existing(self, tmp_ledger):
        existing = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Existing"},
        ]
        write_jsonl(tmp_ledger, existing)
        stats = merge_records(tmp_ledger, [])
        assert stats["inserted"] == 0
        assert stats["updated"] == 0
        result = read_jsonl(tmp_ledger)
        assert len(result) == 1
        assert result[0]["summary"] == "Existing"

    def test_mixed_insert_and_update(self, tmp_ledger):
        existing = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Old"},
        ]
        write_jsonl(tmp_ledger, existing)
        new_records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Updated"},
            {"id": "tracker:PM-999", "dedupe_key": "tracker:PM-999", "summary": "Brand new"},
        ]
        stats = merge_records(tmp_ledger, new_records)
        assert stats["inserted"] == 1
        assert stats["updated"] == 1
        result = read_jsonl(tmp_ledger)
        assert len(result) == 2


class TestReadWriteJsonl:
    def test_read_empty_file(self, tmp_ledger):
        assert read_jsonl(tmp_ledger) == []

    def test_read_nonexistent_file(self, tmp_path):
        assert read_jsonl(tmp_path / "nope.jsonl") == []

    def test_write_and_read_roundtrip(self, tmp_ledger):
        data = [{"a": 1}, {"b": 2}]
        write_jsonl(tmp_ledger, data)
        assert read_jsonl(tmp_ledger) == data
