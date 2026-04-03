"""Shared pytest fixtures for Exoskeleton tests."""
import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "scripts" / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def tracker_fixtures():
    with open(FIXTURES_DIR / "tracker_issues.json") as f:
        return json.load(f)


@pytest.fixture
def intrasearch_fixtures():
    with open(FIXTURES_DIR / "intrasearch_hits.json") as f:
        return json.load(f)


@pytest.fixture
def deepagent_fixtures():
    with open(FIXTURES_DIR / "deepagent_response.json") as f:
        return json.load(f)


@pytest.fixture
def broken_fixtures():
    with open(FIXTURES_DIR / "broken_responses.json") as f:
        return json.load(f)


@pytest.fixture
def sample_aliases():
    return {
        "projects": {
            "navi": ["navigator", "нави", "навигатор"],
            "lumi": ["луми"],
        },
        "people": {
            "sergey-sus": ["сережа сус", "sus", "sergey suslov"],
            "anna-k": ["anna koroleva", "anna k"],
        },
        "queues": {
            "PRACT": ["practicum", "практикум"],
            "LUMI": ["lumi"],
        },
        "abbreviations": {},
    }


@pytest.fixture
def sample_identities():
    return {
        "user": {
            "display_name": "Vlad Kiaune",
            "tracker_login": "vladk",
            "email": "vlad@example.com",
            "teams": ["practicum"],
            "default_queues": ["PRACT", "LUMI"],
        }
    }


@pytest.fixture
def brain_dir(tmp_path):
    """Create a minimal brain directory structure for testing."""
    dirs = [
        "ledger", "views", "views/projects", "views/people", "views/attention",
        "control", "state", "system", "ingest/raw", "ingest/normalized", "ingest/failed",
    ]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)

    for name in [
        "entities.jsonl", "issues.jsonl", "docs.jsonl", "decisions.jsonl",
        "commitments.jsonl", "notes.jsonl", "relations.jsonl", "sync_runs.jsonl",
    ]:
        (tmp_path / "ledger" / name).write_text("")

    (tmp_path / "state" / "source_state.json").write_text(json.dumps({
        "last_sync": {},
        "source_health": {},
    }))
    (tmp_path / "state" / "entity_index.json").write_text(json.dumps({"entities": {}, "aliases": {}}))
    (tmp_path / "state" / "sync_cursor.json").write_text(json.dumps({"cursors": {}}))
    (tmp_path / "state" / "quality_report.json").write_text(json.dumps({
        "last_check": None, "warnings": [], "degraded_sources": [],
    }))

    (tmp_path / "control" / "role.md").write_text("# Role\n\n_Not configured._\n")
    (tmp_path / "control" / "quarter.md").write_text("# Quarter Goals\n\n_Not configured._\n")
    (tmp_path / "control" / "week.md").write_text("# Week Focus\n\n_Not configured._\n")
    (tmp_path / "control" / "constraints.md").write_text("# Constraints\n\n_None._\n")

    return tmp_path
