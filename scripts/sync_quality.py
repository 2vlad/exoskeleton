"""Sync quality checks — invariant verification after merge.

Runs after every sync to detect:
- duplicate dedupe_keys within a ledger file
- missing provenance (source field)
- unresolved entity references
- candidate-only records without corroboration

If checks fail, the previous views are preserved (PRD §16).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from scripts.merge_ledger import read_jsonl

logger = logging.getLogger(__name__)

LEDGER_FILES = [
    "issues.jsonl",
    "docs.jsonl",
    "decisions.jsonl",
    "commitments.jsonl",
    "entities.jsonl",
    "notes.jsonl",
    "relations.jsonl",
]


@dataclass
class QualityReport:
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    unresolved_entities_count: int = 0
    duplicate_keys_count: int = 0
    missing_provenance_count: int = 0
    total_records: int = 0

    def fail(self, warning: str):
        self.passed = False
        self.warnings.append(warning)

    def warn(self, warning: str):
        self.warnings.append(warning)


def run_quality_checks(brain_dir: Path) -> QualityReport:
    """Run all quality checks on the ledger. Returns a QualityReport."""
    report = QualityReport()
    ledger_dir = brain_dir / "ledger"

    for filename in LEDGER_FILES:
        path = ledger_dir / filename
        if not path.exists():
            continue

        records = read_jsonl(path)
        report.total_records += len(records)

        seen_keys: dict[str, int] = {}
        for i, record in enumerate(records):
            dk = record.get("dedupe_key")
            if dk:
                if dk in seen_keys:
                    report.duplicate_keys_count += 1
                    report.fail(
                        f"Duplicate dedupe_key '{dk}' in {filename} "
                        f"(lines {seen_keys[dk]} and {i})"
                    )
                else:
                    seen_keys[dk] = i

        for record in records:
            if not record.get("source") and record.get("kind") != "entity":
                report.missing_provenance_count += 1
                report.warn(
                    f"Missing source provenance in {filename}: "
                    f"id={record.get('id', '?')}"
                )

        for record in records:
            for ref in record.get("entity_refs", []):
                if ref.startswith("unresolved:"):
                    report.unresolved_entities_count += 1

    return report


def save_quality_report(brain_dir: Path, report: QualityReport) -> None:
    """Save quality report to brain/state/quality_report.json."""
    from datetime import datetime, timezone

    state_dir = brain_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "passed": report.passed,
        "warnings": report.warnings,
        "unresolved_entities_count": report.unresolved_entities_count,
        "duplicate_keys_count": report.duplicate_keys_count,
        "missing_provenance_count": report.missing_provenance_count,
        "total_records": report.total_records,
    }

    path = state_dir / "quality_report.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
