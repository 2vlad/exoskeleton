"""Merge normalized records into ledger JSONL files.

Upsert semantics: records are matched by dedupe_key.
- If dedupe_key exists → update (replace entire record).
- If dedupe_key is new → insert.
- Empty new_records NEVER erases existing data (PRD §12.2.5).

Merge is atomic: writes to temp file, then renames.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)


def read_jsonl(path: Path) -> list[dict]:
    """Read all records from a JSONL file."""
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    """Atomically write records to a JSONL file."""
    with NamedTemporaryFile(
        mode="w",
        suffix=".jsonl",
        dir=path.parent,
        delete=False,
        encoding="utf-8",
    ) as tmp:
        for record in records:
            tmp.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        tmp_path = Path(tmp.name)
    tmp_path.rename(path)


def merge_records(ledger_path: Path, new_records: list[dict]) -> dict:
    """Merge new records into existing ledger file by dedupe_key.

    Returns stats dict with inserted/updated counts.
    """
    existing = read_jsonl(ledger_path)

    index: dict[str, int] = {}
    for i, record in enumerate(existing):
        dk = record.get("dedupe_key")
        if dk:
            index[dk] = i

    inserted = 0
    updated = 0

    for record in new_records:
        dk = record.get("dedupe_key")
        if not dk:
            logger.warning("Record missing dedupe_key, skipping: %s", record.get("id"))
            continue

        if dk in index:
            existing[index[dk]] = record
            updated += 1
        else:
            index[dk] = len(existing)
            existing.append(record)
            inserted += 1

    write_jsonl(ledger_path, existing)

    return {"inserted": inserted, "updated": updated, "total": len(existing)}
