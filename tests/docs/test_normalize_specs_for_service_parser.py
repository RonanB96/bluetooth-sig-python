"""Unit tests for scripts/normalize_specs_for_service_parser.py."""

from __future__ import annotations

from pathlib import Path

from scripts import normalize_specs_for_service_parser as normalizer


def test_req_re_matches_conditional_requirements() -> None:
    """Conditional requirement values such as C.1 must be accepted."""
    assert normalizer._REQ_RE.match("C.1")
    assert normalizer._REQ_RE.match("c.2")


def test_extract_rows_from_tables_includes_conditional_requirements() -> None:
    """Table extraction should retain rows with conditional requirements."""
    text = """
| Characteristic | Req | Properties | Security |
|----------------|-----|------------|----------|
| Battery Level | C.1 | Read | N/A |
| Temperature | M | Read | N/A |
"""
    rows = normalizer._extract_rows_from_tables(text)

    assert [row.characteristic for row in rows] == ["Battery Level", "Temperature"]
    assert rows[0].req == "C.1"


def test_normalize_specs_dry_run_does_not_write(tmp_path: Path) -> None:
    """Dry-run mode should report changes without modifying files."""
    spec_file = tmp_path / "battery_service_spec.txt"
    original = "| Battery Level | M | Read | N/A |\n"
    spec_file.write_text(original, encoding="utf-8")

    total, changed, unresolved = normalizer.normalize_specs(tmp_path, "*_spec.txt", dry_run=True)

    assert total == 1
    assert changed == 1
    assert unresolved == 0
    assert spec_file.read_text(encoding="utf-8") == original


def test_normalize_specs_writes_parser_block(tmp_path: Path) -> None:
    """Writable runs should prepend the parser-friendly block."""
    spec_file = tmp_path / "battery_service_spec.txt"
    original = "| Battery Level | M | Read | N/A |\n"
    spec_file.write_text(original, encoding="utf-8")

    _total, changed, unresolved = normalizer.normalize_specs(tmp_path, "*_spec.txt", dry_run=False)

    content = spec_file.read_text(encoding="utf-8")
    assert changed == 1
    assert unresolved == 0
    assert "## Service Characteristics (Parser Format)" in content
    assert "| Battery Level | M | Read | N/A |" in content
    assert content.endswith(original)


def test_normalize_specs_leaves_unresolved_files_unchanged(tmp_path: Path) -> None:
    """Files without extractable rows should remain untouched."""
    spec_file = tmp_path / "empty_service_spec.txt"
    original = "No characteristics table in this file.\n"
    spec_file.write_text(original, encoding="utf-8")

    total, changed, unresolved = normalizer.normalize_specs(tmp_path, "*_spec.txt", dry_run=False)

    assert total == 1
    assert changed == 0
    assert unresolved == 1
    assert spec_file.read_text(encoding="utf-8") == original
