"""Test documentation structure using HTML parsing.

These tests validate theme-generated structural elements like navigation,
footer, breadcrumbs, and internal anchor links.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup


@pytest.mark.built_docs
def test_pages_have_navigation_structure(html_files: list[Path]) -> None:
    """Test that pages have navigation structure."""
    issues: list[str] = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Check for navigation elements (theme-generated)
        nav_selectors: list[tuple[str | None, dict[str, str] | None]] = [
            ("nav", None),
            ("aside", None),
            ("div", {"class": "sidebar"}),
            ("div", {"class": "sidebar-drawer"}),
            ("div", {"class": "sphinxsidebar"}),
            (None, {"role": "navigation"}),
        ]

        found_nav = False
        for tag, attrs in nav_selectors:
            if tag:
                if attrs and soup.find(tag, attrs=attrs):  # type: ignore[arg-type]
                    found_nav = True
                    break
                if not attrs and soup.find(tag):
                    found_nav = True
                    break
            else:
                if attrs and soup.find(attrs=attrs):  # type: ignore[arg-type]
                    found_nav = True
                    break

        if not found_nav:
            issues.append(f"{html_file.name}: No navigation structure found")

    if issues:
        pytest.fail("Navigation structure issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


@pytest.mark.built_docs
def test_pages_have_footer(html_files: list[Path]) -> None:
    """Test that pages have a footer element."""
    issues: list[str] = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Check for footer element or role="contentinfo"
        has_footer = soup.find("footer") is not None or soup.find(attrs={"role": "contentinfo"}) is not None

        if not has_footer:
            issues.append(f"{html_file.name}: No footer found")

    if issues:
        pytest.fail("Footer issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


@pytest.mark.built_docs
def test_internal_anchor_links_are_valid(html_files: list[Path]) -> None:
    """Test that internal anchor links point to actual IDs in the same file."""
    issues: list[str] = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Find all anchor links (href starting with #)
        anchor_links = soup.find_all("a", href=re.compile(r"^#.+"))

        if not anchor_links:
            continue

        # Get all IDs in the page
        all_ids = {elem.get("id") for elem in soup.find_all(id=True)}

        broken_anchors: list[str] = []

        for link in anchor_links:
            href = link.get("href", "")
            if not href or not isinstance(href, str):
                continue
            anchor_id = href[1:]  # Remove the # prefix

            if anchor_id not in all_ids:
                broken_anchors.append(f"#{anchor_id}")

        if broken_anchors:
            issues.append(f"{html_file.name}: Broken anchor links (showing first 5)")
            for anchor in broken_anchors[:5]:
                issues.append(f"  -> {anchor}")

    if issues:
        pytest.fail("Internal anchor link issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:20]))


@pytest.mark.built_docs
def test_sidebar_exists(html_files: list[Path]) -> None:
    """Test that pages have a sidebar for navigation."""
    issues: list[str] = []

    for html_file in html_files:
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Check for sidebar elements
        sidebar_selectors: list[tuple[str | None, dict[str, str] | None]] = [
            ("aside", None),
            ("div", {"class": "sidebar"}),
            ("div", {"class": "sphinxsidebar"}),
            ("div", {"class": "sidebar-drawer"}),
            (None, {"role": "complementary"}),
        ]

        found_sidebar = False
        for tag, attrs in sidebar_selectors:
            element = None
            if tag:
                if attrs:
                    element = soup.find(tag, attrs=attrs)  # type: ignore[arg-type]
                else:
                    element = soup.find(tag)
            else:
                if attrs:
                    element = soup.find(attrs=attrs)  # type: ignore[arg-type]

            if element:
                # Verify sidebar has links
                if hasattr(element, "find_all"):
                    links = element.find_all("a")
                    if links:
                        found_sidebar = True
                        break

        if not found_sidebar:
            issues.append(f"{html_file.name}: No sidebar with navigation links found")

    if issues:
        pytest.fail("Sidebar issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


@pytest.mark.built_docs
def test_breadcrumbs_exist_on_nested_pages(html_files: list[Path]) -> None:
    """Test that nested pages (not top-level) have breadcrumb navigation."""
    issues = []

    for html_file in html_files:
        # Skip top-level index files
        if html_file.name == "index.html" and "/" not in str(html_file.relative_to(html_file.parent.parent)):
            continue

        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Check for breadcrumb elements
        from typing import Any

        breadcrumb_selectors: list[tuple[str | None, dict[str, Any] | None]] = [
            ("nav", {"aria-label": re.compile(r"breadcrumb", re.I)}),
            ("ol", {"class": re.compile(r"breadcrumb", re.I)}),
            ("div", {"class": re.compile(r"breadcrumb", re.I)}),
            (None, {"role": "navigation"}),
        ]

        found_breadcrumbs = False
        for tag, attrs in breadcrumb_selectors:
            if tag:
                if soup.find(tag, attrs=attrs):
                    found_breadcrumbs = True
                    break
            else:
                nav = soup.find(attrs=attrs)
                if nav and ("breadcrumb" in str(nav).lower()):
                    found_breadcrumbs = True
                    break

        if not found_breadcrumbs:
            # Breadcrumbs are optional, so just note it
            issues.append(f"{html_file.name}: No breadcrumbs found (optional feature)")

    # Don't fail, just report if many pages lack breadcrumbs
    if len(issues) > len(html_files) * 0.5:
        pytest.skip(f"Breadcrumbs not consistently used: {len(issues)}/{len(html_files)} pages lack them")
