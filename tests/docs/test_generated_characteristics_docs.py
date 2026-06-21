"""Tests for generated characteristics documentation and docs HTML post-processing."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType, SimpleNamespace

from scripts import generate_char_service_list

_BLUETOOTH_SIG_ASSIGNED_NUMBERS_URL = "https://www.bluetooth.com/specifications/assigned-numbers/"


def _load_docs_conf_module() -> ModuleType:
    """Load the Sphinx conf module without requiring package installation."""
    conf_path = Path(__file__).parent.parent.parent / "docs" / "source" / "conf.py"
    spec = spec_from_file_location("docs_source_conf", conf_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load docs conf module from {conf_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_add_external_link_security_preserves_external_href(tmp_path: Path) -> None:
    """External link hardening must not rewrite the link destination."""
    conf = _load_docs_conf_module()
    html_file = tmp_path / "index.html"
    html_file.write_text(
        (
            '<html><body><a class="reference external" '
            f'href="{_BLUETOOTH_SIG_ASSIGNED_NUMBERS_URL}">Bluetooth SIG</a></body></html>'
        ),
        encoding="utf-8",
    )

    app = SimpleNamespace(outdir=str(tmp_path))
    conf.add_external_link_security(app, None)

    content = html_file.read_text(encoding="utf-8")
    assert f'href="{_BLUETOOTH_SIG_ASSIGNED_NUMBERS_URL}"' in content
    assert 'rel="noopener noreferrer"' in content
    assert "[%22" not in content
