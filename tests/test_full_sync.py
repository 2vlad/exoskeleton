"""Integration test for full 6-phase /sync pipeline.

Simulates a complete first-run sync using fixture data,
verifying that all phases produce correct ledger records
and that the final state is consistent.
"""
import json
from pathlib import Path

import pytest

from scripts.normalize import (
    normalize_tracker_issues,
    normalize_tracker_comments,
    normalize_tracker_links,
    normalize_tracker_goals,
    normalize_intrasearch_hits,
    normalize_calendar_events,
)
from scripts.merge_ledger import merge_records, read_jsonl
from scripts.sync_quality import run_quality_checks
from scripts.rebuild_views import rebuild_active_view, rebuild_all_views
from scripts.extract import extract_issue_keys, extract_dates, extract_urls


class TestPhase1Issues:
    """Phase 1: Tracker issues sync."""

    def test_normalizes_all_issues(self, tracker_fixtures):
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        assert len(issues) == 3
        keys = {i.key for i in issues}
        assert keys == {"PM-123", "PM-456", "LUMI-78"}

    def test_issues_have_provenance(self, tracker_fixtures):
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        for issue in issues:
            assert issue.source == "tracker"
            assert issue.confidence == "canonical"
            assert issue.dedupe_key.startswith("tracker:")
            assert issue.fetched_at

    def test_merges_into_ledger(self, brain_dir, tracker_fixtures):
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        stats = merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [i.model_dump() for i in issues],
        )
        assert stats["inserted"] == 3
        assert stats["total"] == 3


class TestPhase2Comments:
    """Phase 2: Comments on active issues."""

    def test_normalizes_comments(self, tracker_comments_fixtures):
        notes = normalize_tracker_comments(tracker_comments_fixtures["PM-123"], "PM-123")
        assert len(notes) == 2
        assert all(n.source == "tracker" for n in notes)
        assert all(n.source_type == "comment" for n in notes)

    def test_empty_comments_ok(self, tracker_comments_fixtures):
        notes = normalize_tracker_comments(tracker_comments_fixtures["LUMI-78"], "LUMI-78")
        assert len(notes) == 0

    def test_comments_have_entity_refs(self, tracker_comments_fixtures):
        notes = normalize_tracker_comments(tracker_comments_fixtures["PM-123"], "PM-123")
        for note in notes:
            assert "issue:PM-123" in note.entity_refs

    def test_comment_text_extraction(self, tracker_comments_fixtures):
        """Comments contain extractable decisions and dates."""
        notes = normalize_tracker_comments(tracker_comments_fixtures["PM-123"], "PM-123")
        decision_comment = notes[0]
        dates = extract_dates(decision_comment.text)
        assert "2026-04-10" in dates
        urls = extract_urls(notes[1].text)
        assert len(urls) == 1

    def test_merges_comments_into_notes(self, brain_dir, tracker_comments_fixtures):
        all_notes = []
        for issue_key in ["PM-123", "PM-456", "LUMI-78"]:
            notes = normalize_tracker_comments(
                tracker_comments_fixtures[issue_key], issue_key,
            )
            all_notes.extend(notes)
        stats = merge_records(
            brain_dir / "ledger" / "notes.jsonl",
            [n.model_dump() for n in all_notes],
        )
        assert stats["inserted"] == 3  # 2 for PM-123, 1 for PM-456, 0 for LUMI-78


class TestPhase3Links:
    """Phase 3: Issue dependency graph."""

    def test_normalizes_links(self, tracker_links_fixtures):
        rels = normalize_tracker_links(tracker_links_fixtures["PM-123"], "PM-123")
        assert len(rels) == 2

    def test_link_direction(self, tracker_links_fixtures):
        rels = normalize_tracker_links(tracker_links_fixtures["PM-123"], "PM-123")
        # Both are outward from PM-123
        for rel in rels:
            assert rel.from_ref == "issue:PM-123"

    def test_inward_link_reversed(self, tracker_links_fixtures):
        rels = normalize_tracker_links(tracker_links_fixtures["PM-456"], "PM-456")
        assert len(rels) == 1
        rel = rels[0]
        # Inward link: PM-123 → PM-456
        assert rel.from_ref == "issue:PM-123"
        assert rel.to_ref == "issue:PM-456"

    def test_depends_on_mapped(self, tracker_links_fixtures):
        rels = normalize_tracker_links(tracker_links_fixtures["PM-123"], "PM-123")
        depends = [r for r in rels if r.relation_type == "depends_on"]
        assert len(depends) == 1
        assert depends[0].to_ref == "issue:PM-456"

    def test_merges_links_into_relations(self, brain_dir, tracker_links_fixtures):
        all_rels = []
        for issue_key in ["PM-123", "PM-456", "LUMI-78"]:
            rels = normalize_tracker_links(
                tracker_links_fixtures[issue_key], issue_key,
            )
            all_rels.extend(rels)
        stats = merge_records(
            brain_dir / "ledger" / "relations.jsonl",
            [r.model_dump() for r in all_rels],
        )
        assert stats["inserted"] == 4  # 2+1+1
        assert stats["total"] == 4


class TestPhase4Wiki:
    """Phase 4: Wiki pages related to issues."""

    def test_normalizes_wiki_hits(self, intrasearch_fixtures):
        docs = normalize_intrasearch_hits(
            intrasearch_fixtures["doc_results"], query="PM-123 onboarding",
        )
        assert len(docs) == 2
        assert all(d.source == "intrasearch" for d in docs)
        assert all(d.dedupe_key.startswith("intrasearch:") for d in docs)

    def test_wiki_docs_have_urls(self, intrasearch_fixtures):
        docs = normalize_intrasearch_hits(intrasearch_fixtures["doc_results"])
        for doc in docs:
            assert doc.url.startswith("https://")


class TestPhase5Goals:
    """Phase 5: Goals hierarchy."""

    def test_normalizes_goals(self, tracker_goals_fixtures):
        goals, relations = normalize_tracker_goals(tracker_goals_fixtures["goals"])
        assert len(goals) == 2
        keys = {g.key for g in goals}
        assert keys == {"GOAL-1", "GOAL-10"}

    def test_goals_have_type_in_payload(self, tracker_goals_fixtures):
        goals, _ = normalize_tracker_goals(tracker_goals_fixtures["goals"])
        for goal in goals:
            assert goal.payload["type"] == "goal"

    def test_goal_parent_in_entity_refs(self, tracker_goals_fixtures):
        goals, _ = normalize_tracker_goals(tracker_goals_fixtures["goals"])
        child = [g for g in goals if g.key == "GOAL-10"][0]
        assert "goal:GOAL-1" in child.entity_refs

    def test_goal_hierarchy_relations(self, tracker_goals_fixtures):
        _, relations = normalize_tracker_goals(tracker_goals_fixtures["goals"])
        # GOAL-1 → GOAL-10, GOAL-10 → PM-123, GOAL-10 → PM-456
        assert len(relations) == 3
        parent_of = [r for r in relations if r.payload.get("type") == "parent_of"]
        assert len(parent_of) == 3

    def test_goals_merge_alongside_issues(self, brain_dir, tracker_fixtures, tracker_goals_fixtures):
        """Goals and issues coexist in issues.jsonl without collision."""
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [i.model_dump() for i in issues],
        )
        goals, relations = normalize_tracker_goals(tracker_goals_fixtures["goals"])
        stats = merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [g.model_dump() for g in goals],
        )
        # GOAL-1 and GOAL-10 are new; existing issues untouched
        assert stats["inserted"] == 2
        assert stats["total"] == 5  # 3 issues + 2 goals

        ledger = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
        keys = {r["key"] for r in ledger}
        assert keys == {"PM-123", "PM-456", "LUMI-78", "GOAL-1", "GOAL-10"}


class TestPhase6Calendar:
    """Phase 6: Calendar events."""

    def test_normalizes_calendar_events(self, calendar_fixtures):
        notes = normalize_calendar_events(calendar_fixtures["events"])
        assert len(notes) == 2
        assert all(n.source == "calendar" for n in notes)
        assert all(n.dedupe_key.startswith("cal:") for n in notes)

    def test_calendar_attendees_in_entity_refs(self, calendar_fixtures):
        notes = normalize_calendar_events(calendar_fixtures["events"])
        sync_event = notes[0]
        assert "person:vladk" in sync_event.entity_refs
        assert "person:sergey-sus" in sync_event.entity_refs

    def test_calendar_payload_has_details(self, calendar_fixtures):
        notes = normalize_calendar_events(calendar_fixtures["events"])
        event = notes[0]
        assert event.payload["name"] == "Weekly Product Sync"
        assert event.payload["start"]
        assert len(event.payload["attendees"]) == 3


class TestFullSyncPipeline:
    """End-to-end: all 6 phases in sequence, then quality + views."""

    def test_full_sync_first_run(
        self,
        brain_dir,
        tracker_fixtures,
        tracker_comments_fixtures,
        tracker_links_fixtures,
        intrasearch_fixtures,
        tracker_goals_fixtures,
        calendar_fixtures,
    ):
        """Simulate a complete /sync first run and verify final state."""

        # --- Phase 1: Issues ---
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [i.model_dump() for i in issues],
        )

        # --- Phase 2: Comments ---
        all_notes = []
        for issue in issues:
            comments = normalize_tracker_comments(
                tracker_comments_fixtures.get(issue.key, []), issue.key,
            )
            all_notes.extend(comments)

        # --- Phase 3: Links ---
        all_relations = []
        for issue in issues:
            links = normalize_tracker_links(
                tracker_links_fixtures.get(issue.key, []), issue.key,
            )
            all_relations.extend(links)

        # --- Phase 4: Wiki ---
        all_docs = []
        for issue in issues:
            docs = normalize_intrasearch_hits(
                intrasearch_fixtures["doc_results"],
                query=f"{issue.key} {issue.summary}",
            )
            all_docs.extend(docs)

        # --- Phase 5: Goals ---
        goals, goal_relations = normalize_tracker_goals(tracker_goals_fixtures["goals"])
        merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [g.model_dump() for g in goals],
        )
        all_relations.extend(goal_relations)

        # --- Phase 6: Calendar ---
        calendar_notes = normalize_calendar_events(calendar_fixtures["events"])
        all_notes.extend(calendar_notes)

        # --- Merge all into ledger ---
        merge_records(
            brain_dir / "ledger" / "notes.jsonl",
            [n.model_dump() for n in all_notes],
        )
        merge_records(
            brain_dir / "ledger" / "relations.jsonl",
            [r.model_dump() for r in all_relations],
        )
        # Docs from wiki — deduplicated by URL
        unique_docs = {d.dedupe_key: d for d in all_docs}
        merge_records(
            brain_dir / "ledger" / "docs.jsonl",
            [d.model_dump() for d in unique_docs.values()],
        )

        # --- Quality check ---
        report = run_quality_checks(brain_dir)
        assert report.passed, f"Quality check failed: {report.warnings}"
        assert report.duplicate_keys_count == 0

        # --- Verify ledger contents ---
        issues_ledger = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
        notes_ledger = read_jsonl(brain_dir / "ledger" / "notes.jsonl")
        relations_ledger = read_jsonl(brain_dir / "ledger" / "relations.jsonl")
        docs_ledger = read_jsonl(brain_dir / "ledger" / "docs.jsonl")

        # 3 issues + 2 goals = 5
        assert len(issues_ledger) == 5
        issue_keys = {r["key"] for r in issues_ledger}
        assert "PM-123" in issue_keys
        assert "GOAL-1" in issue_keys
        assert "GOAL-10" in issue_keys

        # 3 comments + 2 calendar events = 5
        assert len(notes_ledger) == 5
        comment_notes = [n for n in notes_ledger if n.get("source_type") == "comment"]
        calendar_notes_l = [n for n in notes_ledger if n.get("source_type") == "calendar_event"]
        assert len(comment_notes) == 3
        assert len(calendar_notes_l) == 2

        # 4 issue links + 3 goal relations = 7
        assert len(relations_ledger) == 7

        # 2 unique wiki docs (same docs found for each issue, deduplicated)
        assert len(docs_ledger) == 2

        # --- Rebuild views ---
        results = rebuild_all_views(brain_dir)
        assert results["active"] > 0

        active_md = rebuild_active_view(brain_dir)
        assert "PM-123" in active_md
        assert "PM-456" in active_md
        assert "GOAL-1" in active_md

    def test_full_sync_idempotent(
        self,
        brain_dir,
        tracker_fixtures,
        tracker_comments_fixtures,
        tracker_links_fixtures,
        tracker_goals_fixtures,
        calendar_fixtures,
    ):
        """Running full sync twice produces identical ledger state."""
        for _ in range(2):
            issues = normalize_tracker_issues(tracker_fixtures["normal"])
            merge_records(
                brain_dir / "ledger" / "issues.jsonl",
                [i.model_dump() for i in issues],
            )

            all_notes = []
            all_relations = []
            for issue in issues:
                all_notes.extend(
                    normalize_tracker_comments(
                        tracker_comments_fixtures.get(issue.key, []), issue.key,
                    )
                )
                all_relations.extend(
                    normalize_tracker_links(
                        tracker_links_fixtures.get(issue.key, []), issue.key,
                    )
                )

            goals, goal_rels = normalize_tracker_goals(tracker_goals_fixtures["goals"])
            merge_records(
                brain_dir / "ledger" / "issues.jsonl",
                [g.model_dump() for g in goals],
            )
            all_relations.extend(goal_rels)
            all_notes.extend(normalize_calendar_events(calendar_fixtures["events"]))

            merge_records(brain_dir / "ledger" / "notes.jsonl", [n.model_dump() for n in all_notes])
            merge_records(brain_dir / "ledger" / "relations.jsonl", [r.model_dump() for r in all_relations])

        # After 2 runs, counts should be same as 1 run
        assert len(read_jsonl(brain_dir / "ledger" / "issues.jsonl")) == 5
        assert len(read_jsonl(brain_dir / "ledger" / "notes.jsonl")) == 5
        assert len(read_jsonl(brain_dir / "ledger" / "relations.jsonl")) == 7

    def test_partial_phase_failure_preserves_other_phases(
        self,
        brain_dir,
        tracker_fixtures,
        tracker_comments_fixtures,
        calendar_fixtures,
    ):
        """If one phase fails (e.g., links), other phases' data is preserved."""
        # Phase 1: Issues — succeeds
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [i.model_dump() for i in issues],
        )

        # Phase 2: Comments — succeeds
        all_notes = []
        for issue in issues:
            all_notes.extend(
                normalize_tracker_comments(
                    tracker_comments_fixtures.get(issue.key, []), issue.key,
                )
            )
        merge_records(brain_dir / "ledger" / "notes.jsonl", [n.model_dump() for n in all_notes])

        # Phase 3: Links — "fails" (empty data, simulating MCP failure)
        merge_records(brain_dir / "ledger" / "relations.jsonl", [])

        # Phase 6: Calendar — succeeds
        cal_notes = normalize_calendar_events(calendar_fixtures["events"])
        merge_records(
            brain_dir / "ledger" / "notes.jsonl",
            [n.model_dump() for n in cal_notes],
        )

        # Verify: issues + comments + calendar OK, relations empty
        assert len(read_jsonl(brain_dir / "ledger" / "issues.jsonl")) == 3
        assert len(read_jsonl(brain_dir / "ledger" / "notes.jsonl")) == 5  # 3 comments + 2 calendar
        assert len(read_jsonl(brain_dir / "ledger" / "relations.jsonl")) == 0

        report = run_quality_checks(brain_dir)
        assert report.passed
