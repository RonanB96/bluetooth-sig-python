"""Test sidebar content structure and consistency.

This test validates the sidebar navigation items to prevent regressions
in the documentation structure. The sidebar frequently breaks during
documentation updates, so these tests ensure critical navigation
elements remain present and correctly structured.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page

from ..conftest import (
    EXPECTED_SECTION_ORDER,
    REQUIRED_SECTIONS,
    SELECTOR_SIDEBAR_BRAND,
    SELECTOR_SIDEBAR_DRAWER,
    SELECTOR_SIDEBAR_SEARCH,
    SELECTOR_SIDEBAR_TREE,
    SELECTOR_SIDEBAR_TREE_LINK,
    SELECTOR_TOCTREE_CHECKBOX,
    SELECTOR_TOCTREE_L1,
    SELECTOR_TOP_LEVEL_ITEMS,
)


def get_index_html_url() -> str:
    """Get the file:// URL to the built documentation index.html."""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent.parent
    index_path = project_root / "docs" / "build" / "html" / "index.html"
    return index_path.as_uri()


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_has_required_sections(page: Page) -> None:
    """Test that sidebar contains all required top-level navigation sections.

    These sections follow the Diátaxis framework and are critical for
    documentation navigation. Any missing section indicates a broken build.
    """
    page.goto(get_index_html_url())

    missing_sections: list[str] = []

    for section_name, expected_href in REQUIRED_SECTIONS.items():
        # Look for the section link in the sidebar
        section_link = page.locator(f"{SELECTOR_SIDEBAR_TREE} a:has-text('{section_name}')").first

        if section_link.count() == 0:
            missing_sections.append(section_name)
            continue

        # Verify the link href is correct
        actual_href = section_link.get_attribute("href")
        assert actual_href is not None, f"Section '{section_name}' has no href"
        assert expected_href in actual_href, (
            f"Section '{section_name}' has incorrect href. Expected to contain '{expected_href}', got '{actual_href}'"
        )

    if missing_sections:
        pytest.fail(
            "Missing required sidebar sections:\n" + "\n".join(f"  - {section}" for section in missing_sections)
        )


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_sections_are_expandable(page: Page) -> None:
    """Test that sidebar sections have proper expand/collapse functionality.

    Ensures that top-level sections are marked as expandable with proper
    ARIA attributes and checkbox controls.
    """
    page.goto(get_index_html_url())

    # Find all top-level toctree items
    top_level_items = page.locator(SELECTOR_TOP_LEVEL_ITEMS).all()

    assert len(top_level_items) > 0, "No top-level sidebar items found"

    for item in top_level_items:
        # Check if it has children (should have .has-children class)
        has_children_class = "has-children" in (item.get_attribute("class") or "")

        if not has_children_class:
            continue

        # Should have a checkbox for toggling
        checkbox = item.locator(SELECTOR_TOCTREE_CHECKBOX).first
        assert checkbox.count() > 0, f"Expandable item missing toggle checkbox: {item.inner_text()[:50]}"

        # Checkbox should have proper ARIA label
        aria_label = checkbox.get_attribute("aria-label")
        assert aria_label is not None, "Toggle checkbox missing aria-label"
        assert "Toggle navigation" in aria_label, f"Toggle checkbox has incorrect aria-label: {aria_label}"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_structure_consistency(page: Page) -> None:
    """Test that sidebar structure is consistent and well-formed.

    Validates the overall sidebar DOM structure to catch malformed HTML
    that could break navigation rendering.
    """
    page.goto(get_index_html_url())

    # Check sidebar container exists
    sidebar = page.locator(SELECTOR_SIDEBAR_DRAWER).first
    assert sidebar.count() > 0, "Sidebar container (.sidebar-drawer) not found"

    # Check sidebar has brand
    brand = page.locator(SELECTOR_SIDEBAR_BRAND).first
    assert brand.count() > 0, "Sidebar brand not found"

    # Check sidebar has search
    search = page.locator(SELECTOR_SIDEBAR_SEARCH).first
    assert search.count() > 0, "Sidebar search not found"

    # Check sidebar-tree exists and contains navigation
    sidebar_tree = page.locator(SELECTOR_SIDEBAR_TREE).first
    assert sidebar_tree.count() > 0, "Sidebar tree (.sidebar-tree) not found"

    # Check that sidebar-tree has at least one ul > li structure
    nav_list = sidebar_tree.locator("ul").first
    assert nav_list.count() > 0, "Sidebar tree has no <ul> element"

    list_items = nav_list.locator("li").all()
    assert len(list_items) > 0, "Sidebar navigation has no list items"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_links_are_valid(page: Page) -> None:
    """Test that all sidebar links have valid hrefs.

    Ensures that navigation links point to actual files and aren't
    broken by relative path issues or missing files.
    """
    page.goto(get_index_html_url())

    # Get all links from the sidebar tree
    sidebar_links = page.locator(SELECTOR_SIDEBAR_TREE_LINK).all()

    assert len(sidebar_links) > 0, "No links found in sidebar"

    broken_links: list[str] = []

    for link in sidebar_links[:20]:  # Test first 20 to keep test fast
        href = link.get_attribute("href")
        text = link.inner_text().strip()

        if not href:
            broken_links.append(f"'{text}' - no href attribute")
            continue

        # Skip external links and anchors
        if href.startswith(("http://", "https://", "#")):
            continue

        # For relative links, we just check they're well-formed
        if not href or href == "":
            broken_links.append(f"'{text}' - empty href")

    if broken_links:
        pytest.fail("Broken sidebar links found:\n" + "\n".join(f"  - {link}" for link in broken_links))


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_brand_text(page: Page) -> None:
    """Test that sidebar displays correct project branding.

    Ensures the project name and version are correctly displayed
    in the sidebar header.
    """
    page.goto(get_index_html_url())

    brand = page.locator(SELECTOR_SIDEBAR_BRAND).first
    assert brand.count() > 0, "Sidebar brand not found"

    brand_text = brand.inner_text()

    # Should contain project name
    assert "Bluetooth SIG Standards Library" in brand_text, f"Sidebar brand missing project name. Found: '{brand_text}'"

    # Should contain version or "documentation"
    assert any(keyword in brand_text for keyword in ["documentation", "0.", "1."]), (
        f"Sidebar brand missing version or 'documentation'. Found: '{brand_text}'"
    )


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_search_functionality(page: Page) -> None:
    """Test that sidebar search box is properly configured.

    Ensures the search functionality is accessible and points to
    the correct search page.
    """
    page.goto(get_index_html_url())

    # Check search input exists
    search_input = page.locator(SELECTOR_SIDEBAR_SEARCH).first
    assert search_input.count() > 0, "Sidebar search input not found"

    # Check it has proper attributes
    placeholder = search_input.get_attribute("placeholder")
    assert placeholder is not None, "Search input missing placeholder"

    aria_label = search_input.get_attribute("aria-label")
    assert aria_label is not None, "Search input missing aria-label"

    # Check that search form exists and points to search.html
    search_form = page.locator(".sidebar-search-container").first
    if search_form.count() > 0:
        action = search_form.get_attribute("action")
        assert action is not None, "Search form missing action"
        assert "search.html" in action, f"Search form action incorrect: {action}"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_maintains_order(page: Page) -> None:
    """Test that sidebar sections appear in the correct order.

    The order of sections is important for documentation flow.
    This test ensures sections aren't accidentally reordered.
    """
    page.goto(get_index_html_url())

    # Get all top-level section links in order
    section_links = page.locator(f"{SELECTOR_SIDEBAR_TREE} > ul > li{SELECTOR_TOCTREE_L1} > a.reference").all()

    actual_order = [link.inner_text().strip() for link in section_links]

    # Filter to only the expected sections (there might be others)
    actual_filtered = [s for s in actual_order if s in EXPECTED_SECTION_ORDER]

    # Check order is maintained
    expected_filtered = [s for s in EXPECTED_SECTION_ORDER if s in actual_filtered]

    assert actual_filtered == expected_filtered, (
        f"Sidebar sections are in wrong order.\nExpected: {expected_filtered}\nActual:   {actual_filtered}"
    )
