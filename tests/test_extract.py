import pytest
from scripts.extract import (
    extract_issue_keys,
    extract_dates,
    extract_urls,
    extract_tracker_logins,
)


class TestExtractIssueKeys:
    def test_basic_keys(self):
        text = "Check PM-123 and LUMI-78 for details"
        assert extract_issue_keys(text) == ["PM-123", "LUMI-78"]

    def test_no_keys(self):
        assert extract_issue_keys("no keys here") == []

    def test_keys_from_deepagent_response(self):
        text = "PM-123\nPM-456\nPM-100\nLUMI-78\nPRACT-500"
        keys = extract_issue_keys(text)
        assert len(keys) == 5
        assert "PRACT-500" in keys

    def test_deduplicates(self):
        text = "PM-123 mentioned again PM-123"
        assert extract_issue_keys(text) == ["PM-123"]


class TestExtractDates:
    def test_iso_date(self):
        assert extract_dates("due 2026-06-30 end") == ["2026-06-30"]

    def test_no_dates(self):
        assert extract_dates("no dates here") == []


class TestExtractUrls:
    def test_wiki_url(self):
        text = "see https://wiki.yandex-team.ru/practicum/onboarding/ for details"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert "wiki.yandex-team.ru" in urls[0]

    def test_multiple_urls(self):
        text = "https://a.com and https://b.com"
        assert len(extract_urls(text)) == 2


class TestExtractTrackerLogins:
    def test_assignee_field(self):
        logins = extract_tracker_logins({"assignee": {"id": "vladk"}, "reporter": {"id": "anna-k"}})
        assert "vladk" in logins
        assert "anna-k" in logins

    def test_string_assignee(self):
        logins = extract_tracker_logins({"assignee": "vladk"})
        assert "vladk" in logins
