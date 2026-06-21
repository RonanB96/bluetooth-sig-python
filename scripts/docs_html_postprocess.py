"""HTML post-processing helpers for built Sphinx documentation."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

_EXTERNAL_LINK_PATTERN = re.compile(r'<a\s+[^>]*href=["\'](https?://[^"\']*)["\'][^>]*>')
_REL_SECURITY_PATTERN = re.compile(r'\brel=["\'][^"\']*\b(noopener|noreferrer)\b')
_REL_VALUE_PATTERN = re.compile(r'\brel=["\']([^"\']*)["\']')


def _add_security_attrs(match: re.Match[str]) -> str:
    """Insert or extend rel security attributes on one external anchor tag."""
    full_tag = match.group(0)
    href = match.group(1)

    if "localhost" in href or "127.0.0.1" in href:
        return full_tag

    if _REL_SECURITY_PATTERN.search(full_tag):
        return full_tag

    href_pattern = r'href=["\']' + re.escape(href) + r'["\']'
    rel_match = _REL_VALUE_PATTERN.search(full_tag)

    if rel_match:
        old_rel = rel_match.group(0)
        rel_value = rel_match.group(1)
        new_rel_value = f"{rel_value} noopener noreferrer" if rel_value else "noopener noreferrer"
        new_rel = f'rel="{new_rel_value}"'
        return full_tag.replace(old_rel, new_rel, 1)

    href_attr = re.search(href_pattern, full_tag)
    if href_attr is None:
        return full_tag

    return full_tag.replace(href_attr.group(0), f'{href_attr.group(0)} rel="noopener noreferrer"', 1)


def apply_external_link_security(
    build_dir: Path,
    *,
    warn: Callable[[str], None] | None = None,
) -> tuple[int, int]:
    """Add rel='noopener noreferrer' to external links in built HTML files.

    Prevents tabnabbing attacks by ensuring external links cannot access
    window.opener. This is a defense-in-depth measure even though modern
    browsers automatically apply noopener to target='_blank' links.

    Args:
        build_dir: Directory containing built HTML output.
        warn: Optional callback for non-fatal per-file failures.

    Returns:
        Tuple of (files_changed, links_processed).
    """
    fixed_count = 0
    total_links = 0

    for html_file in build_dir.rglob("*.html"):
        try:
            content = html_file.read_text(encoding="utf-8")
            original_content = content

            def counting_replacer(match: re.Match[str]) -> str:
                nonlocal total_links
                total_links += 1
                return _add_security_attrs(match)

            content = _EXTERNAL_LINK_PATTERN.sub(counting_replacer, content)

            if content != original_content:
                html_file.write_text(content, encoding="utf-8")
                fixed_count += 1
        except OSError as exc:
            message = f"Warning: Failed to add security attributes to {html_file}: {exc}"
            if warn is not None:
                warn(message)
            else:
                print(message)

    return fixed_count, total_links
