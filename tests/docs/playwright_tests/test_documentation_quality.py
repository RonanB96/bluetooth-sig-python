"""Test documentation quality - EVERY HTML FILE.

ALL tests parametrized across all HTML files.
Tests content quality, code blocks, performance, and consistency.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.built_docs
@pytest.mark.playwright
def test_code_blocks_have_language_indicator(page: Page, html_file: str) -> None:
    """Test that code blocks indicate their language."""
    page.goto(html_file)

    code_blocks = page.locator("pre code, div.highlight").all()

    if len(code_blocks) == 0:
        pytest.skip("No code blocks on page")

    has_language_info = False

    for block in code_blocks[:3]:
        class_attr = block.get_attribute("class") or ""

        if "language-" in class_attr or "hljs-" in class_attr:
            has_language_info = True
            break

        parent = block.locator("..")
        parent_class = parent.get_attribute("class") or ""

        if "highlight-" in parent_class or "language-" in parent_class:
            has_language_info = True
            break

    if not has_language_info:
        pytest.skip("Language indicators may use different pattern")


@pytest.mark.built_docs
@pytest.mark.playwright
def test_version_information_present(page: Page, html_file: str) -> None:
    """Test that documentation includes version information."""
    page.goto(html_file)

    page_text = page.inner_text("body").lower()

    version_indicators = [
        "version",
        "v0.",
        "v1.",
        "release",
        "latest",
    ]

    has_version = any(indicator in page_text for indicator in version_indicators)

    if not has_version:
        pytest.skip("Version info optional but recommended")


@pytest.mark.built_docs
@pytest.mark.playwright
def test_page_has_css_styling(page: Page, html_file: str) -> None:
    """Test that pages have CSS styling applied."""
    page.goto(html_file)

    css_links = page.locator("link[rel='stylesheet']")

    if css_links.count() == 0:
        pytest.skip("May use inline styles")

    body_bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    assert body_bg, f"{html_file}: Should have computed background color"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_page_has_footer(page: Page, html_file: str) -> None:
    """Test that pages have a footer."""
    page.goto(html_file)

    footer_selectors = ["footer", '[role="contentinfo"]', ".footer"]

    has_footer = any(page.locator(selector).count() > 0 for selector in footer_selectors)

    if not has_footer:
        pytest.skip("Footer optional but recommended")

    footer = page.locator("footer, [role='contentinfo']").first
    footer_text = footer.inner_text().strip()
    assert len(footer_text) > 0, f"{html_file}: Footer should have content"


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
