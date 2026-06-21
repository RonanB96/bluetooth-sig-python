#!/usr/bin/env python3
"""Normalise extracted spec files for service-table parsing.

This script prepends a canonical, parser-friendly Service Characteristics table
to each ``*_spec.txt`` file in a target directory.

The normalisation is non-destructive: original file content is preserved and only
an additional block is inserted when not already present.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import msgspec

_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root / "src"))

_REQ_RE = re.compile(r"^(M|O|X|N/A|N\\A|C\.\d+)$", re.IGNORECASE)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_PARENS_RE = re.compile(r"\([^)]*\)")

_SERVICE_NAME_SCAN_LINES = 120
_NOTE_SCAN_LINES = 60


class NormalizedRow(msgspec.Struct, kw_only=True, frozen=True):
    """Normalized characteristic row for canonical table."""

    characteristic: str
    req: str
    properties: str
    security: str


def _normalize_name(value: str) -> str:
    cleaned = _PARENS_RE.sub("", value.lower())
    return _NON_ALNUM_RE.sub("", cleaned)


def _guess_service_name(text: str, stem: str) -> str:
    lines = text.splitlines()
    for line in lines[:_SERVICE_NAME_SCAN_LINES]:
        match = re.search(r"^[-*]?\s*Full\s+name\s*:\s*(.+)$", line.strip(), re.IGNORECASE)
        if match:
            return re.sub(r"\s+Service$", "", match.group(1).strip(), flags=re.IGNORECASE)

    header = lines[0].strip() if lines else stem
    header = re.sub(r"\s*v\d[\w.\-]*$", "", header, flags=re.IGNORECASE)
    header = re.sub(r"\([^)]*\)", "", header)
    header = re.sub(r"\s+SERVICE$", "", header, flags=re.IGNORECASE)
    header = re.sub(r"\s+Service$", "", header, flags=re.IGNORECASE)
    header = header.strip(" #=-")
    if header:
        return header

    return stem.split("_", maxsplit=1)[0]


def _extract_rows_from_tables(text: str) -> list[NormalizedRow]:
    rows: list[NormalizedRow] = []
    seen: set[str] = set()

    for line in text.splitlines():
        if "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue

        first = parts[0]
        second = parts[1]

        first_lower = first.lower()
        second_lower = second.lower()

        if first_lower in {"characteristic", "name"} or second_lower in {"req", "requirement"}:
            continue
        if re.fullmatch(r"[\-: ]+", first) and re.fullmatch(r"[\-: ]+", second):
            continue
        if first_lower.startswith("0x"):
            continue
        if "descriptor" in first_lower or "ccc" in first_lower:
            continue

        req = second.split()[0]
        if not _REQ_RE.match(req):
            continue

        properties = parts[2] if len(parts) >= 3 else "N/A"
        security = parts[-1] if len(parts) >= 4 else "N/A"

        key = _normalize_name(first)
        if not key or key in seen:
            continue

        rows.append(
            NormalizedRow(
                characteristic=first,
                req=req.upper(),
                properties=properties,
                security=security,
            )
        )
        seen.add(key)

    return rows


def _extract_from_note_list(text: str) -> list[NormalizedRow]:
    for line in text.splitlines()[:_NOTE_SCAN_LINES]:
        note_match = re.search(r"NOTE:\s*Characteristics\s+(.+?)\s+defined\s+here", line, re.IGNORECASE)
        if not note_match:
            continue

        raw_items = note_match.group(1)
        candidates = [item.strip(" .") for item in raw_items.split(",")]
        rows = [
            NormalizedRow(
                characteristic=item.replace("_", " ").title(),
                req="O",
                properties="N/A",
                security="N/A",
            )
            for item in candidates
            if item
        ]
        if rows:
            return rows

    return []


def _canonical_block(service_name: str, rows: list[NormalizedRow], source: str) -> str:
    header = [
        "## Service Characteristics (Parser Format)",
        f"Source for normalization: {source}",
        f"Service Name: {service_name}",
        "| Characteristic | Req | Properties | Security |",
        "|----------------|-----|------------|----------|",
    ]
    for row in rows:
        header.append(f"| {row.characteristic} | {row.req} | {row.properties} | {row.security} |")

    return "\n".join(header) + "\n\n"


def normalize_specs(spec_dir: Path, pattern: str, dry_run: bool) -> tuple[int, int, int]:
    """Normalize all matching spec files.

    Returns:
        Tuple of (total_files, changed_files, unresolved_files)
    """
    files = sorted(path for path in spec_dir.glob(pattern) if path.is_file())

    changed = 0
    unresolved = 0

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")

        if "## Service Characteristics (Parser Format)" in content:
            continue

        rows = _extract_rows_from_tables(content)
        source = "existing table rows"

        if not rows:
            rows = _extract_from_note_list(content)
            source = "NOTE characteristics list"

        if not rows:
            unresolved += 1
            continue

        service_name = _guess_service_name(content, file_path.stem)
        block = _canonical_block(service_name, rows, source)
        new_content = block + content

        if not dry_run:
            file_path.write_text(new_content, encoding="utf-8")
        changed += 1

    return len(files), changed, unresolved


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Normalize extracted spec files for parser compatibility")
    parser.add_argument(
        "--spec-dir",
        type=Path,
        default=_project_root / ".tmp",
        help="Directory containing extracted spec files",
    )
    parser.add_argument("--pattern", default="*_spec.txt", help="Glob pattern for spec files")
    parser.add_argument("--dry-run", action="store_true", help="Report potential changes without writing files")
    args = parser.parse_args()

    total, changed, unresolved = normalize_specs(args.spec_dir, args.pattern, args.dry_run)

    print("Spec normalization summary")
    print("=" * 40)
    print(f"Total files    : {total}")
    print(f"Changed files  : {changed}")
    print(f"Unresolved     : {unresolved}")
    print(f"Mode           : {'dry-run' if args.dry_run else 'write'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
