import pytest
from scripts.entity_resolver import EntityResolver


@pytest.fixture
def aliases():
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
        },
        "abbreviations": {},
    }


@pytest.fixture
def identities():
    return {
        "user": {
            "tracker_login": "vladk",
            "display_name": "Vlad Kiaune",
            "email": "vlad@example.com",
        }
    }


@pytest.fixture
def resolver(aliases, identities):
    return EntityResolver(aliases=aliases, identities=identities)


class TestExactMatch:
    def test_exact_id(self, resolver):
        result = resolver.resolve("sergey-sus", kind="person")
        assert result.resolved_id == "person:sergey-sus"
        assert result.confidence == "exact"

    def test_exact_alias(self, resolver):
        result = resolver.resolve("sus", kind="person")
        assert result.resolved_id == "person:sergey-sus"
        assert result.confidence == "alias"

    def test_case_insensitive_alias(self, resolver):
        result = resolver.resolve("Sergey Suslov", kind="person")
        assert result.resolved_id == "person:sergey-sus"

    def test_project_alias(self, resolver):
        result = resolver.resolve("навигатор", kind="project")
        assert result.resolved_id == "project:navi"


class TestAmbiguous:
    def test_unknown_name(self, resolver):
        result = resolver.resolve("unknown person xyz", kind="person")
        assert result.confidence == "unresolved"
        assert result.resolved_id is None


class TestQueue:
    def test_queue_alias(self, resolver):
        result = resolver.resolve("practicum", kind="queue")
        assert result.resolved_id == "queue:PRACT"

    def test_queue_direct(self, resolver):
        result = resolver.resolve("PRACT", kind="queue")
        assert result.resolved_id == "queue:PRACT"
