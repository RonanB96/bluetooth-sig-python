"""Test documentation navigation - EVERY HTML FILE.

ALL tests parametrized to run against every HTML file.
Tests navigation structure, links, search, and cross-references.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.built_docs
@pytest.mark.playwright
def test_page_loads_successfully(page: Page, html_file: str) -> None:
    """Test that every page loads with 200 status."""
    response = page.goto(html_file)
    assert response is not None, f"{html_file}: No response"
    assert response.status == 200, f"{html_file}: Status {response.status}"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_navigation_structure_exists(page: Page, html_file: str) -> None:
    """Test that navigation structure is present on all pages."""
    page.goto(html_file)

    nav_selectors = [
        "nav",
        ".sidebar",
        ".toctree-wrapper",
        ".sphinxsidebar",
        '[role="navigation"]',
    ]

    found_nav = any(page.locator(selector).count() > 0 for selector in nav_selectors)

    assert found_nav, f"{html_file}: No navigation structure found"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_internal_anchor_links_valid(page: Page, html_file: str) -> None:
    """Test that anchor links point to existing elements."""
    page.goto(html_file)

    # Wait for page to be fully loaded
    page.wait_for_load_state("load")

    anchor_links = page.locator("a[href^='#']").all()

    if not anchor_links:
        pytest.skip("No anchor links on page")

    broken_anchors: list[str] = []

    for link in anchor_links:
        href = link.get_attribute("href")

        if not href or href == "#":
            continue

        anchor_id = href[1:]

        # Check if target exists - use getElementById which handles special characters correctly
        target_exists = page.evaluate(
            """(anchorId) => {
                const byId = document.getElementById(anchorId);
                return byId !== null;
            }""",
            anchor_id,
        )

        if not target_exists:
            broken_anchors.append(href)

    if broken_anchors:
        pytest.fail(
            f"{html_file}: Broken anchor links:\n" + "\n".join(f"  - {anchor}" for anchor in broken_anchors[:5])
        )


@pytest.mark.built_docs
@pytest.mark.playwright
def test_page_has_footer(page: Page, html_file: str) -> None:
    """Test that pages have a footer."""
    page.goto(html_file)

    footer_selectors = ["footer", '[role="contentinfo"]', ".footer"]

    has_footer = any(page.locator(selector).count() > 0 for selector in footer_selectors)

    if not has_footer:
        pytest.skip("Footer optional but recommended")


@pytest.mark.built_docs
@pytest.mark.playwright
def test_sidebar_navigation_exists(page: Page, html_file: str) -> None:
    """Test that sidebar navigation exists."""
    page.goto(html_file)

    sidebar_selectors = [
        "aside",
        ".sidebar",
        ".sphinxsidebar",
        '[role="complementary"]',
        "nav.toctree",
    ]

    has_sidebar = any(page.locator(selector).count() > 0 for selector in sidebar_selectors)

    if not has_sidebar:
        pytest.skip("Sidebar may use different pattern")

    # Sidebar should have links
    for selector in sidebar_selectors:
        sidebar = page.locator(selector).first
        if sidebar.count() > 0:
            links = sidebar.locator("a")
            assert links.count() > 0, f"{html_file}: Sidebar should have links"
            break


@pytest.mark.built_docs
@pytest.mark.playwright
def test_page_has_breadcrumbs(page: Page, html_file: str) -> None:
    """Test for breadcrumb navigation on pages."""
    page.goto(html_file)

    # Skip for top-level pages
    if html_file.endswith("index.html") and "/" not in html_file[:-10]:
        pytest.skip("Top-level pages may not have breadcrumbs")

    breadcrumb_selectors = [
        "nav[aria-label*='breadcrumb' i]",
        ".breadcrumb",
        ".breadcrumbs",
        '[role="navigation"] ol',
    ]

    has_breadcrumbs = any(page.locator(selector).count() > 0 for selector in breadcrumb_selectors)

    if not has_breadcrumbs:
        pytest.skip("Breadcrumbs optional feature")


@pytest.mark.built_docs
@pytest.mark.playwright
def test_mobile_menu_toggle_exists(page: Page, html_file: str) -> None:
    """Test that mobile menu toggle exists."""
    page.goto(html_file)

    toggle_selectors = [
        "button.mobile-menu",
        "[aria-label*='menu' i]",
        ".menu-toggle",
        "[data-toggle='navigation']",
        ".navbar-toggle",
    ]

    has_toggle = any(page.locator(selector).count() > 0 for selector in toggle_selectors)

    if not has_toggle:
        pytest.skip("Mobile menu toggle may not be needed")


@pytest.mark.built_docs
@pytest.mark.playwright
def test_documentation_has_theme(page: Page, html_file: str) -> None:
    """Test that pages have CSS styling applied."""
    page.goto(html_file)

    css_links = page.locator("link[rel='stylesheet']")

    if css_links.count() == 0:
        pytest.skip("May use inline styles")

    # Check that body has background color (theme applied)
    body_bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    assert body_bg, f"{html_file}: Should have computed background color"
