#!/usr/bin/env python3
"""Validate service characteristic coverage against extracted Bluetooth SIG specs.

This script parses service characteristic tables from extracted spec text files
and compares them to service implementations in ``src/bluetooth_sig/gatt/services``.

Expected spec file format:
- One file per spec in a directory (default: ``.tmp``)
- Filenames ending with ``_spec.txt``
- A characteristics section containing a table with at least:
  characteristic name and requirement columns

Exit codes:
- 0: All matched services are aligned and every parsed spec mapped to a service
- 1: At least one matched service has mismatches or a parsed spec could not be matched
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import msgspec

# Ensure src is importable when running as a script
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root / "src"))

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic  # noqa: E402
from bluetooth_sig.gatt.characteristics.registry import get_characteristic_class_map  # noqa: E402
from bluetooth_sig.gatt.services.base import BaseGattService  # noqa: E402
from bluetooth_sig.gatt.services.registry import get_service_class_map  # noqa: E402
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName  # noqa: E402

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_REQ_MANDATORY_RE = re.compile(r"^M$", re.IGNORECASE)
_SEPARATOR_ROW_RE = re.compile(r"^[\s\-|:]+$")
_PARENS_RE = re.compile(r"\([^)]*\)")

_TOKEN_ALIASES: dict[str, str] = {
    "config": "configuration",
    "ctrl": "control",
    "cp": "controlpoint",
    "racp": "recordaccesscontrolpoint",
    "rccp": "reconnectionconfigurationcontrolpoint",
    "ccid": "contentcontrolid",
    "cte": "constanttoneextension",
    "pres": "presentation",
    "fmt": "format",
    "desc": "descriptor",
    "properties": "attribute",
    "setting": "settings",
}

_GENERIC_PLACEHOLDER_ROWS = {
    "ess characteristic",
    "uds characteristic",
    "uds characteristics",
    "imd measurement",
}

_STOP_TOKENS = {"characteristic", "service", "specification", "v", "extract", "extracted", "reference"}

MIN_EMPTY_STREAK_TO_END_BLOCK = 3
MIN_TABLE_COLUMN_COUNT = 2
MIN_FALLBACK_OVERLAP = 2
MIN_FALLBACK_RATIO = 0.4
_SERVICE_NAME_SCAN_LINES = 80


class SpecCharacteristic(msgspec.Struct, kw_only=True, frozen=True):
    """A characteristic row parsed from a spec table."""

    name: str
    requirement: str

    @property
    def is_required(self) -> bool:
        """Return True when the requirement is mandatory (M)."""
        return bool(_REQ_MANDATORY_RE.match(self.requirement.strip()))


class SpecTable(msgspec.Struct, kw_only=True, frozen=True):
    """Parsed characteristics table for one spec file."""

    file_path: Path
    service_name: str
    characteristics: tuple[SpecCharacteristic, ...]


class ServiceComparison(msgspec.Struct, kw_only=True, frozen=True):
    """Comparison result for one mapped spec-to-service pair."""

    spec_table: SpecTable
    service_name: ServiceName
    missing_in_implementation: tuple[str, ...]
    extra_in_implementation: tuple[str, ...]
    requirement_mismatches: tuple[str, ...]
    unimplemented_characteristic_classes: tuple[str, ...]

    @property
    def is_ok(self) -> bool:
        """Return True when no mismatches were found."""
        return (
            not self.missing_in_implementation
            and not self.extra_in_implementation
            and not self.requirement_mismatches
            and not self.unimplemented_characteristic_classes
        )


def _normalize_name(value: str) -> str:
    cleaned = _PARENS_RE.sub("", value.lower())
    cleaned = cleaned.replace("pres.format", "presentation format")
    cleaned = cleaned.replace("current elapsed time", "elapsed time")
    tokens = [token for token in _NON_ALNUM_RE.split(cleaned) if token]
    normalized_tokens: list[str] = []
    for token in tokens:
        normalized = _TOKEN_ALIASES.get(token, token)
        if normalized in _STOP_TOKENS:
            continue
        normalized_tokens.append(normalized)
    return "".join(normalized_tokens)


def _to_title_words(value: str) -> str:
    words = [word for word in re.split(r"[^A-Za-z0-9]+", value) if word]
    return " ".join(word.capitalize() for word in words)


def _guess_service_name(lines: list[str], file_stem: str) -> str:
    for line in lines[:_SERVICE_NAME_SCAN_LINES]:
        stripped = line.strip()
        if not stripped:
            continue

        service_name_match = re.search(r"^Service\s+Name\s*:\s*(.+)$", stripped, re.IGNORECASE)
        if service_name_match:
            return service_name_match.group(1).strip()

        full_name_match = re.search(r"^[-*]?\s*Full\s+name\s*:\s*(.+)$", stripped, re.IGNORECASE)
        if full_name_match:
            return re.sub(r"\s+Service$", "", full_name_match.group(1).strip(), flags=re.IGNORECASE)

    header = lines[0].strip() if lines else file_stem
    header = re.sub(r"\s*v\d[\w.\-]*$", "", header, flags=re.IGNORECASE)
    header = re.sub(r"\([^)]*\)", "", header)
    header = re.sub(r"\s+SERVICE$", "", header, flags=re.IGNORECASE)
    header = re.sub(r"\s+Service$", "", header, flags=re.IGNORECASE)
    header = header.strip(" =")
    if header:
        return _to_title_words(header)

    stem_prefix = file_stem.split("_", maxsplit=1)[0]
    return _to_title_words(stem_prefix)


def _find_table_block(lines: list[str], heading_pattern: re.Pattern[str]) -> list[str]:
    start_index = -1
    for index, line in enumerate(lines):
        if heading_pattern.search(line):
            start_index = index
            break

    if start_index < 0:
        return []

    block_lines: list[str] = []
    empty_streak = 0
    for line in lines[start_index + 1 :]:
        stripped = line.strip()

        if stripped:
            empty_streak = 0
        else:
            empty_streak += 1

        if stripped.startswith("#") and block_lines:
            break

        if (
            stripped
            and stripped.isupper()
            and "CHARACTERISTICS" not in stripped
            and "TABLE" not in stripped
            and block_lines
        ):
            break

        if empty_streak >= MIN_EMPTY_STREAK_TO_END_BLOCK and block_lines:
            break

        block_lines.append(line)

    return block_lines


def _parse_table_rows(block_lines: list[str]) -> tuple[SpecCharacteristic, ...]:
    rows: list[SpecCharacteristic] = []
    in_characteristics_table = False

    for line in block_lines:
        if "|" not in line:
            if in_characteristics_table and rows:
                break
            continue

        raw_columns = [column.strip() for column in line.split("|")]
        columns = [column for column in raw_columns if column]
        if len(columns) < MIN_TABLE_COLUMN_COUNT:
            continue

        first_col = columns[0]
        req_col = columns[1]

        if _SEPARATOR_ROW_RE.match(first_col) and _SEPARATOR_ROW_RE.match(req_col):
            continue

        first_col_lower = first_col.lower()
        req_col_lower = req_col.lower()

        if first_col_lower.startswith("characteristic") and req_col_lower in {"req", "requirement"}:
            in_characteristics_table = True
            continue

        if req_col_lower in {"req", "requirement"}:
            continue

        if not in_characteristics_table:
            continue

        requirement = req_col.split()[0]
        if not re.match(r"^(M|O|X|N/A|N\\A|C\.\d+)$", requirement, flags=re.IGNORECASE):
            continue

        lower_name = first_col_lower
        if lower_name.startswith("0x"):
            continue
        if "descriptor" in lower_name or "ccc" in lower_name:
            continue
        if re.search(r"\bdesc\b", lower_name):
            continue
        if lower_name.endswith(" opcode"):
            continue
        if lower_name in _GENERIC_PLACEHOLDER_ROWS:
            continue

        rows.append(
            SpecCharacteristic(
                name=first_col,
                requirement=requirement,
            )
        )

    return tuple(rows)


def _parse_spec_table(file_path: Path) -> SpecTable | None:
    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    lines = text.splitlines()
    if not lines:
        return None

    characteristics_rows: list[SpecCharacteristic] = []

    main_header_re = re.compile(r"\bCHARACTERISTICS\b\s*\(", re.IGNORECASE)
    main_block = _find_table_block(lines, main_header_re)
    if main_block:
        characteristics_rows.extend(_parse_table_rows(main_block))

    additional_header_re = re.compile(r"^\s*ADDITIONAL\s+CHARACTERISTICS\s*\([^)]*table", re.IGNORECASE)
    additional_block = _find_table_block(lines, additional_header_re)
    if additional_block:
        characteristics_rows.extend(_parse_table_rows(additional_block))

    # Fallback: if no heading-based block found, try parsing the whole file directly.
    if not characteristics_rows:
        characteristics_rows.extend(_parse_table_rows(lines))

    # Deduplicate by normalized characteristic name while preserving first occurrence.
    deduped_rows: dict[str, SpecCharacteristic] = {}
    for row in characteristics_rows:
        key = _normalize_name(row.name)
        deduped_rows.setdefault(key, row)

    characteristics = tuple(deduped_rows.values())
    if not characteristics:
        return None

    service_name = _guess_service_name(lines, file_path.stem)
    return SpecTable(file_path=file_path, service_name=service_name, characteristics=characteristics)


def _build_service_characteristics_map() -> dict[ServiceName, dict[CharacteristicName, bool]]:
    service_map: dict[ServiceName, dict[CharacteristicName, bool]] = {}
    service_classes: dict[ServiceName, type[BaseGattService]] = get_service_class_map()
    for service_name, service_cls in service_classes.items():
        service_characteristics = service_cls.__dict__.get("service_characteristics", {})
        service_map[service_name] = dict(service_characteristics)
    return service_map


def _match_service(
    spec_table: SpecTable, service_chars: dict[ServiceName, dict[CharacteristicName, bool]]
) -> ServiceName | None:
    spec_service_key = _normalize_name(spec_table.service_name)
    for service_name in service_chars:
        if _normalize_name(service_name.value) == spec_service_key:
            return service_name

    spec_char_keys = {_normalize_name(row.name) for row in spec_table.characteristics}
    if not spec_char_keys:
        return None

    best_match: ServiceName | None = None
    best_overlap = 0
    best_ratio = 0.0
    best_match_count = 0

    for service_name, impl_chars in service_chars.items():
        impl_char_keys = {_normalize_name(enum_member.value) for enum_member in impl_chars}
        overlap = len(spec_char_keys & impl_char_keys)
        ratio = overlap / len(spec_char_keys)
        if overlap > best_overlap or (overlap == best_overlap and ratio > best_ratio):
            best_overlap = overlap
            best_ratio = ratio
            best_match = service_name
            best_match_count = 1
        elif overlap == best_overlap and ratio == best_ratio and overlap > 0:
            best_match_count += 1

    if best_match is None:
        return None

    if best_match_count > 1:
        return None

    # Fallback matching should be conservative to avoid accidental mappings.
    if best_overlap < MIN_FALLBACK_OVERLAP or best_ratio < MIN_FALLBACK_RATIO:
        return None

    return best_match


def _compare_service(
    spec_table: SpecTable,
    service_name: ServiceName,
    impl_chars: dict[CharacteristicName, bool],
    char_class_map: dict[CharacteristicName, type[BaseCharacteristic[Any]]],
) -> ServiceComparison:
    spec_by_norm = {_normalize_name(row.name): row for row in spec_table.characteristics}
    impl_by_norm = {
        _normalize_name(enum_member.value): (enum_member, is_required)
        for enum_member, is_required in impl_chars.items()
    }

    missing = tuple(sorted(row.name for key, row in spec_by_norm.items() if key not in impl_by_norm))

    extra = tuple(
        sorted(
            enum_member.value
            for key, (enum_member, _is_required) in impl_by_norm.items()
            if key not in spec_by_norm
        )
    )

    req_mismatches: list[str] = []
    for key, row in spec_by_norm.items():
        impl_entry = impl_by_norm.get(key)
        if impl_entry is None:
            continue
        enum_member, impl_required = impl_entry
        if row.is_required != impl_required:
            req_mismatches.append(
                f"{row.name}: spec={row.requirement} "
                f"expected_required={row.is_required} impl_required={impl_required} ({enum_member.name})"
            )

    unimplemented_classes = tuple(
        sorted(enum_member.value for enum_member in impl_chars if enum_member not in char_class_map)
    )

    return ServiceComparison(
        spec_table=spec_table,
        service_name=service_name,
        missing_in_implementation=missing,
        extra_in_implementation=extra,
        requirement_mismatches=tuple(sorted(req_mismatches)),
        unimplemented_characteristic_classes=unimplemented_classes,
    )


def _iter_spec_files(spec_dir: Path, pattern: str) -> list[Path]:
    return sorted(path for path in spec_dir.glob(pattern) if path.is_file())


def main(spec_dir: Path, pattern: str, verbose: bool) -> int:
    """Run service characteristic validation.

    Args:
        spec_dir: Directory containing extracted spec files
        pattern: Glob pattern for spec files
        verbose: Print per-file parse skips and matched details

    Returns:
        Process exit code
    """
    spec_files = _iter_spec_files(spec_dir, pattern)
    if not spec_files:
        print(f"No spec files found in {spec_dir} matching pattern '{pattern}'.")
        return 0

    service_chars = _build_service_characteristics_map()
    char_class_map = get_characteristic_class_map()

    parsed_tables: list[SpecTable] = []
    skipped_files: list[Path] = []
    for file_path in spec_files:
        parsed = _parse_spec_table(file_path)
        if parsed is None:
            skipped_files.append(file_path)
            continue
        parsed_tables.append(parsed)

    comparisons: list[ServiceComparison] = []
    unmatched_specs: list[SpecTable] = []

    for spec_table in parsed_tables:
        matched_service = _match_service(spec_table, service_chars)
        if matched_service is None:
            unmatched_specs.append(spec_table)
            continue
        comparisons.append(
            _compare_service(
                spec_table=spec_table,
                service_name=matched_service,
                impl_chars=service_chars[matched_service],
                char_class_map=char_class_map,
            )
        )

    failures = [comparison for comparison in comparisons if not comparison.is_ok]

    print("\nService Characteristics Validation")
    print("=" * 72)
    print(f"Spec files scanned      : {len(spec_files)}")
    print(f"Spec tables parsed      : {len(parsed_tables)}")
    print(f"Specs matched to service: {len(comparisons)}")
    print(f"Unmatched specs         : {len(unmatched_specs)}")
    print(f"Parse skips             : {len(skipped_files)}")
    print(f"Service mismatches      : {len(failures)}")

    if verbose and skipped_files:
        print("\nSkipped (no parseable characteristics table):")
        for file_path in skipped_files:
            print(f"  - {file_path.name}")

    if unmatched_specs:
        print("\nUnmatched spec tables:")
        for spec_table in unmatched_specs:
            print(f"  - {spec_table.file_path.name}: service='{spec_table.service_name}'")

    if failures:
        print("\nMismatches:")
        for comparison in failures:
            print(
                f"\n[{comparison.spec_table.file_path.name}] "
                f"spec='{comparison.spec_table.service_name}' -> impl='{comparison.service_name.value}'"
            )
            if comparison.missing_in_implementation:
                print("  Missing in implementation:")
                for item in comparison.missing_in_implementation:
                    print(f"    - {item}")
            if comparison.extra_in_implementation:
                print("  Extra in implementation:")
                for item in comparison.extra_in_implementation:
                    print(f"    - {item}")
            if comparison.requirement_mismatches:
                print("  Requirement flag mismatches:")
                for item in comparison.requirement_mismatches:
                    print(f"    - {item}")
            if comparison.unimplemented_characteristic_classes:
                print("  Service references characteristics without class implementation:")
                for item in comparison.unimplemented_characteristic_classes:
                    print(f"    - {item}")
    elif comparisons:
        print("\nAll matched services are aligned with parsed spec characteristic tables.")

    return 1 if failures or unmatched_specs else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate service characteristic definitions against extracted spec tables"
    )
    parser.add_argument(
        "--spec-dir",
        type=Path,
        default=_project_root / ".tmp",
        help="Directory containing extracted spec text files (default: ./.tmp)",
    )
    parser.add_argument(
        "--pattern",
        default="*_spec.txt",
        help="Glob pattern used to find spec files (default: *_spec.txt)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print skipped files and extra details")
    cli_args = parser.parse_args()
    raise SystemExit(main(spec_dir=cli_args.spec_dir, pattern=cli_args.pattern, verbose=cli_args.verbose))
