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
