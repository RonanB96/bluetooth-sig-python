"""Tests for generated characteristics documentation."""

from __future__ import annotations

from pathlib import Path

from scripts import generate_char_service_list


def test_generated_characteristics_docs_include_registry_coverage() -> None:
    """Generated reference docs should describe implementation coverage accurately."""
    markdown = generate_char_service_list.generate_markdown()
    committed_markdown = Path("docs/source/reference/characteristics.md").read_text(encoding="utf-8")
    (
        implemented_characteristics,
        total_characteristics,
        missing_characteristics,
        implemented_services,
        total_services,
        missing_services,
    ) = generate_char_service_list.get_coverage_summary()
    sig_sha, sig_commit_url = generate_char_service_list.get_sig_submodule_context()

    assert committed_markdown == markdown
    assert f"**{implemented_characteristics} of {total_characteristics}**" in markdown
    assert f"**{implemented_services} of {total_services}**" in markdown
    if sig_sha != "unknown":
        assert f"[`{sig_sha[:7]}`]({sig_commit_url})" in markdown
    if missing_characteristics:
        assert "## Not Yet Implemented Characteristics" in markdown
        for characteristic in missing_characteristics:
            assert characteristic in markdown
    else:
        assert "## Not Yet Implemented Characteristics" not in markdown

    if missing_services:
        assert "## Not Yet Implemented Services" in markdown
        for service in missing_services:
            assert service in markdown
    else:
        assert "## Not Yet Implemented Services" not in markdown
