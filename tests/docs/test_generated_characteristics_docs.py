"""Tests for generated characteristics documentation."""

from __future__ import annotations

from scripts import generate_char_service_list


def test_generated_characteristics_docs_include_registry_coverage() -> None:
    """Generated reference docs should describe implementation coverage accurately."""
    markdown = generate_char_service_list.generate_markdown()
    (
        implemented_characteristics,
        total_characteristics,
        missing_characteristics,
        implemented_services,
        total_services,
        missing_services,
    ) = generate_char_service_list.get_coverage_summary()
    sig_sha, sig_commit_url = generate_char_service_list.get_sig_submodule_context()

    assert f"**{implemented_characteristics} of {total_characteristics}**" in markdown
    assert f"**{implemented_services} of {total_services}**" in markdown
    if sig_sha != "unknown":
        assert f"[`{sig_sha[:7]}`]({sig_commit_url})" in markdown
    assert "## Not Yet Implemented Characteristics" in markdown
    assert "## Not Yet Implemented Services" in markdown
    if missing_characteristics:
        assert missing_characteristics[0] in markdown
    if missing_services:
        assert missing_services[0] in markdown
