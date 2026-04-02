import json
import pytest
from pathlib import Path
from scripts.normalize import normalize_tracker_issue, normalize_intrasearch_hit, normalize_tracker_issues


FIXTURES = Path(__file__).parent.parent / "scripts" / "fixtures"


class TestNormalizeTrackerIssue:
    def test_normal_issue(self):
        with open(FIXTURES / "tracker_issues.json") as f:
            data = json.load(f)
        raw = data["normal"][0]
        issue = normalize_tracker_issue(raw)
        assert issue.key == "PM-123"
        assert issue.summary == "Implement onboarding flow for new users"
        assert issue.status == "inProgress"
        assert issue.assignee == "vladk"
        assert issue.queue == "PM"
        assert issue.source == "tracker"
        assert issue.confidence == "canonical"
        assert issue.dedupe_key == "tracker:PM-123"
        assert issue.id == "tracker:PM-123"

    def test_all_normal_issues(self):
        with open(FIXTURES / "tracker_issues.json") as f:
            data = json.load(f)
        issues = normalize_tracker_issues(data["normal"])
        assert len(issues) == 3
        keys = {i.key for i in issues}
        assert keys == {"PM-123", "PM-456", "LUMI-78"}

    def test_malformed_issue_skipped(self):
        with open(FIXTURES / "broken_responses.json") as f:
            data = json.load(f)
        results = normalize_tracker_issues(data["partial_list"])
        assert len(results) == 1
        assert results[0].key == "PM-123"


class TestNormalizeIntrasearchHit:
    def test_doc_hit(self):
        with open(FIXTURES / "intrasearch_hits.json") as f:
            data = json.load(f)
        hit = data["doc_results"][0]
        doc = normalize_intrasearch_hit(hit, query="onboarding")
        assert doc.title == "Onboarding Flow Design Doc"
        assert doc.source == "intrasearch"
        assert doc.query == "onboarding"
        assert doc.confidence == "canonical"
