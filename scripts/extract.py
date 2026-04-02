"""Tier A — deterministic extraction from text and structured data.

Uses regex/rules/mappings for:
- Issue keys (PROJ-123 pattern)
- Dates (ISO format)
- URLs
- Tracker logins from structured fields

No LLM involved. This is the most reliable extraction tier.
"""
from __future__ import annotations

import re

_ISSUE_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
_ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_URL_RE = re.compile(r"https?://[^\s)\]>\"']+")


def extract_issue_keys(text: str) -> list[str]:
    """Extract unique issue keys from text, preserving order of first occurrence."""
    seen = set()
    result = []
    for match in _ISSUE_KEY_RE.finditer(text):
        key = match.group(1)
        if key not in seen:
            seen.add(key)
            result.append(key)
    return result


def extract_dates(text: str) -> list[str]:
    """Extract ISO dates (YYYY-MM-DD) from text."""
    return _ISO_DATE_RE.findall(text)


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return _URL_RE.findall(text)


def extract_tracker_logins(raw: dict) -> list[str]:
    """Extract tracker logins from structured issue data."""
    logins = []
    for field_name in ("assignee", "reporter", "createdBy", "updatedBy"):
        value = raw.get(field_name)
        if isinstance(value, dict):
            login = value.get("id") or value.get("login")
            if login:
                logins.append(login)
        elif isinstance(value, str) and value:
            logins.append(value)

    for follower in raw.get("followers", []):
        if isinstance(follower, dict):
            login = follower.get("id") or follower.get("login")
            if login:
                logins.append(login)
        elif isinstance(follower, str):
            logins.append(follower)

    return list(dict.fromkeys(logins))
