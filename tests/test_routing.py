import pytest
from scripts.routing import route_record, RoutingError


class TestRouting:
    def test_issue_routes_to_issues_jsonl(self):
        assert route_record("issue") == "issues.jsonl"

    def test_document_routes_to_docs_jsonl(self):
        assert route_record("document") == "docs.jsonl"

    def test_decision_routes(self):
        assert route_record("decision") == "decisions.jsonl"

    def test_commitment_routes(self):
        assert route_record("commitment") == "commitments.jsonl"

    def test_entity_routes(self):
        assert route_record("entity") == "entities.jsonl"

    def test_note_routes(self):
        assert route_record("note") == "notes.jsonl"

    def test_relation_routes(self):
        assert route_record("relation") == "relations.jsonl"

    def test_sync_run_routes(self):
        assert route_record("sync_run") == "sync_runs.jsonl"

    def test_unknown_kind_raises(self):
        with pytest.raises(RoutingError):
            route_record("unknown_kind")
