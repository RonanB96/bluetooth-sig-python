"""Tests for scripts/docs_html_postprocess.py."""

from __future__ import annotations

from pathlib import Path

from scripts.docs_html_postprocess import apply_external_link_security

_BLUETOOTH_SIG_ASSIGNED_NUMBERS_URL = "https://www.bluetooth.com/specifications/assigned-numbers/"


def test_apply_external_link_security_preserves_external_href(tmp_path: Path) -> None:
    """External link hardening must not rewrite the link destination."""
    html_file = tmp_path / "index.html"
    html_file.write_text(
        (
            '<html><body><a class="reference external" '
            f'href="{_BLUETOOTH_SIG_ASSIGNED_NUMBERS_URL}">Bluetooth SIG</a></body></html>'
        ),
        encoding="utf-8",
    )

    fixed_count, total_links = apply_external_link_security(tmp_path)

    content = html_file.read_text(encoding="utf-8")
    assert fixed_count == 1
    assert total_links == 1
    assert f'href="{_BLUETOOTH_SIG_ASSIGNED_NUMBERS_URL}"' in content
    assert 'rel="noopener noreferrer"' in content
    assert "[%22" not in content


def test_apply_external_link_security_skips_localhost(tmp_path: Path) -> None:
    """Localhost links should not receive security rel attributes."""
    html_file = tmp_path / "index.html"
    html_file.write_text(
        '<html><body><a href="http://127.0.0.1:8000/">local</a></body></html>',
        encoding="utf-8",
    )

    fixed_count, total_links = apply_external_link_security(tmp_path)

    content = html_file.read_text(encoding="utf-8")
    assert fixed_count == 0
    assert total_links == 1
    assert 'rel="noopener noreferrer"' not in content
