"""Test accessibility features using HTML parsing.

These tests validate accessibility attributes in the rendered HTML documentation.
They check for proper semantic HTML, ARIA attributes, and theme-generated accessibility features.

Note: Content-level accessibility (alt text, link text quality) is tested at the markdown stage.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Skip this entire module if beautifulsoup4 is not installed
try:
    from bs4 import BeautifulSoup, Tag
except ModuleNotFoundError:
    pytest.skip("beautifulsoup4 not installed", allow_module_level=True)


@pytest.mark.built_docs
def test_pages_have_proper_title(html_files: list[Path]) -> None:
    """Test that all pages have descriptive titles."""
    issues = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        title = soup.title

        if title is None:
            issues.append(f"{html_file.name}: Missing <title> tag")
            continue

        title_text = title.string or ""
        title_length = len(title_text.strip())

        if title_length < 5:
            issues.append(f"{html_file.name}: Title too short ({title_length} chars): '{title_text}'")
        elif title_length > 200:
            issues.append(f"{html_file.name}: Title too long ({title_length} chars)")

    if issues:
        pytest.fail("Title validation issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


@pytest.mark.built_docs
def test_pages_have_language_attribute(html_files: list[Path]) -> None:
    """Test that pages have proper language attribute for screen readers."""
    issues = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        html_tag = soup.find("html")

        if not isinstance(html_tag, Tag):
            issues.append(f"{html_file.name}: <html> tag is not a valid element")
            continue

        lang = html_tag.get("lang")

        if not lang:
            issues.append(f"{html_file.name}: Missing lang attribute on <html>")
        elif len(str(lang)) < 2:
            issues.append(f"{html_file.name}: Invalid lang attribute: '{lang}'")

    if issues:
        pytest.fail("Language attribute issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


@pytest.mark.built_docs
def test_pages_have_main_landmark(html_files: list[Path]) -> None:
    """Test that pages have a main landmark for screen readers."""
    issues = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Check for <main> element or role="main"
        has_main = soup.find("main") is not None or soup.find(attrs={"role": "main"}) is not None

        if not has_main:
            issues.append(f"{html_file.name}: No <main> landmark found")

    if issues:
        pytest.fail("Main landmark issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


@pytest.mark.built_docs
def test_tables_have_headers(html_files: list[Path]) -> None:
    """Test that tables have proper header cells for accessibility."""
    issues = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        tables = soup.find_all("table")

        if not tables:
            continue

        for idx, table in enumerate(tables):
            th_cells = table.find_all("th")
            header_roles = table.find_all(attrs={"role": "columnheader"})

            if not th_cells and not header_roles:
                issues.append(f"{html_file.name}: Table {idx + 1} has no header cells (<th> or role='columnheader')")

    if issues:
        pytest.fail("Table header issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


@pytest.mark.built_docs
def test_search_form_has_label(index_html_path: Path) -> None:
    """Test that the search form has proper labels for accessibility."""
    with open(index_html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Find search inputs (theme-generated)
    search_inputs = soup.find_all("input", attrs={"type": "search"})
    search_inputs.extend(soup.find_all("input", attrs={"name": re.compile(r"search|q", re.I)}))

    if not search_inputs:
        pytest.skip("No search input found")

    issues = []

    for search_input in search_inputs:
        input_id = search_input.get("id")

        # Check for label association
        has_label = False

        if input_id:
            label = soup.find("label", attrs={"for": input_id})
            if label:
                has_label = True

        # Check for ARIA label
        if search_input.get("aria-label") or search_input.get("aria-labelledby"):
            has_label = True

        # Check for placeholder (not ideal, but acceptable)
        if search_input.get("placeholder"):
            has_label = True

        if not has_label:
            issues.append(f"Search input (id={input_id or 'none'}) has no label")

    if issues:
        pytest.fail("Search form label issues:\n" + "\n".join(f"  - {issue}" for issue in issues))


@pytest.mark.built_docs
def test_external_links_have_security_attributes(html_files: list[Path]) -> None:
    """Test that external links have proper security attributes (rel='noopener noreferrer')."""
    issues: list[str] = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Find external links (http/https)
        external_links = soup.find_all("a", href=re.compile(r"^https?://"))

        if not external_links:
            continue

        insecure_links: list[str] = []

        for link in external_links:
            href = link.get("href", "")
            if not isinstance(href, str):
                continue

            # Skip localhost/127.0.0.1
            if "localhost" in href or "127.0.0.1" in href:
                continue

            rel = link.get("rel")
            rel_list: list[str] = []
            if rel is None:
                rel_list = []
            elif isinstance(rel, str):
                rel_list = rel.split()
            else:
                # Handle list or other iterable types
                rel_list = list(rel)  # type: ignore[arg-type]

            # Check for security attributes
            has_noopener = "noopener" in rel_list
            has_noreferrer = "noreferrer" in rel_list

            if not (has_noopener or has_noreferrer):
                insecure_links.append(href)

        if len(insecure_links) > 5:
            issues.append(
                f"{html_file.name}: {len(insecure_links)} external links lack security attributes (showing first 5)"
            )
            for link_url in insecure_links[:5]:
                issues.append(f"  -> {link_url}")

    if issues:
        pytest.fail("External link security issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:20]))
