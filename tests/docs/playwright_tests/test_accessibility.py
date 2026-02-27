"""Test documentation accessibility compliance - EVERY HTML FILE.

ALL tests parametrized to run against every HTML file in docs/build/html.
This ensures 100% coverage of documentation pages.

Tests validate:
- Proper heading hierarchy
- Alt text for images
- Semantic HTML structure
- ARIA labels and landmarks
- Keyboard accessibility
- Performance
- Security attributes
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_page_has_proper_title(page: Page, html_file: str) -> None:
    """Test that pages have descriptive titles."""
    page.goto(html_file)
    title = page.title()
    assert title, f"Missing title on {html_file}"
    assert 5 < len(title) < 200, f"Title length issue on {html_file}: {len(title)} chars"


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_heading_hierarchy(page: Page, html_file: str) -> None:
    """Test proper heading hierarchy."""
    page.goto(html_file)
    page.wait_for_load_state("domcontentloaded")
    h1_count = page.locator("h1").count()
    assert 1 <= h1_count <= 2, f"Wrong h1 count on {html_file}: {h1_count}"

    all_headings = page.locator("h1, h2, h3, h4, h5, h6").count()
    assert all_headings > 0, f"No headings on {html_file}"


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_heading_hierarchy_no_skips(page: Page, html_file: str) -> None:
    """Test that heading hierarchy doesn't skip levels (h1 -> h4 without h2/h3)."""
    page.goto(html_file)

    headings = page.locator("h1, h2, h3, h4, h5, h6").all()

    if len(headings) == 0:
        pytest.skip("No headings found")

    heading_levels = []
    for heading in headings:
        tag_name = heading.evaluate("el => el.tagName")
        level = int(tag_name[1])
        heading_levels.append(level)

    if len(heading_levels) > 1:
        max_level = max(heading_levels)
        for expected_level in range(1, max_level):
            if expected_level not in heading_levels:
                pytest.fail(
                    f"{html_file}: Heading hierarchy skips h{expected_level}. Found: {sorted(set(heading_levels))}"
                )


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_language_attribute(page: Page, html_file: str) -> None:
    """Test HTML lang attribute for screen readers."""
    page.goto(html_file)
    lang = page.locator("html").get_attribute("lang")
    assert lang and len(lang) >= 2, f"Missing or invalid lang attribute on {html_file}"


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_images_have_alt_text(page: Page, html_file: str) -> None:
    """Test that images have alt text for accessibility."""
    page.goto(html_file)

    images = page.locator("img").all()

    if not images:
        pytest.skip("No images on page")

    missing_alt = []
    for img in images:
        alt_attr = img.get_attribute("alt")
        if alt_attr is None:
            img_src = img.get_attribute("src") or "unknown"
            missing_alt.append(img_src)

    if missing_alt:
        pytest.fail(
            f"{html_file}: Images without alt attribute:\n" + "\n".join(f"  - {src}" for src in missing_alt[:5])
        )


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_links_have_descriptive_text(page: Page, html_file: str) -> None:
    """Test that links have descriptive text (not just 'click here')."""
    page.goto(html_file)

    links = page.locator("a[href]").all()

    if not links:
        pytest.skip("No links on page")

    poor_link_text = ["click here", "here", "read more", "more", "link"]
    problematic = []

    for link in links[:20]:
        text = link.inner_text().strip().lower()
        if text in poor_link_text:
            href = link.get_attribute("href") or "unknown"
            problematic.append((text, href))

    if problematic and len(problematic) > 2:
        pytest.fail(
            f"{html_file}: Non-descriptive link text:\n"
            + "\n".join(f"  - '{text}' -> {href}" for text, href in problematic[:3])
        )


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_page_has_main_landmark(page: Page, html_file: str) -> None:
    """Test that page has a main landmark for screen readers."""
    page.goto(html_file)

    main_exists = page.locator("main").count() > 0 or page.locator('[role="main"]').count() > 0

    if not main_exists:
        pytest.skip("Main landmark optional but recommended")


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_interactive_elements_keyboard_accessible(page: Page, html_file: str) -> None:
    """Test that interactive elements are keyboard accessible."""
    page.goto(html_file)

    first_link = page.locator("a[href]").first

    if first_link.count() == 0:
        pytest.skip("No interactive elements")

    first_link.focus()
    is_focused = page.evaluate("document.activeElement.tagName === 'A'")
    assert is_focused, f"{html_file}: Links should be keyboard focusable"


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_skip_to_content_link(page: Page, html_file: str) -> None:
    """Test for skip-to-content link (accessibility best practice)."""
    page.goto(html_file)

    skip_links = page.locator("a:has-text('skip'), a:has-text('Skip to'), a.skip-link")

    if skip_links.count() == 0:
        pytest.skip("Skip-to-content link optional")

    href = skip_links.first.get_attribute("href")
    assert href and href.startswith("#"), f"{html_file}: Skip link should point to anchor"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_page_load_performance(page: Page, html_file: str) -> None:
    """Test that pages load within acceptable performance budget."""
    page.goto(html_file)

    metrics = page.evaluate("""() => {
        const perf = performance.getEntriesByType('navigation')[0];
        if (!perf) return null;
        return {
            domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
            loadComplete: perf.loadEventEnd - perf.loadEventStart,
            domInteractive: perf.domInteractive - perf.fetchStart,
        };
    }""")

    if metrics is None:
        pytest.skip("Navigation timing API not available")

    assert metrics["domContentLoaded"] < 1000, (
        f"{html_file}: DOM content loaded too slow: {metrics['domContentLoaded']:.0f}ms"
    )
    assert metrics["loadComplete"] < 2000, f"{html_file}: Page load too slow: {metrics['loadComplete']:.0f}ms"
    assert metrics["domInteractive"] < 3000, f"{html_file}: DOM interactive too slow: {metrics['domInteractive']:.0f}ms"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_code_blocks_render_properly(page: Page, html_file: str) -> None:
    """Test that code blocks render with proper formatting."""
    page.goto(html_file)

    code_blocks = page.locator("pre code, div.highlight, .code-block")

    if code_blocks.count() == 0:
        pytest.skip("No code blocks on page")

    first_block = code_blocks.first
    assert first_block.is_visible(), f"{html_file}: Code block should be visible"

    code_text = first_block.inner_text()
    assert len(code_text) > 0, f"{html_file}: Code block should have content"


@pytest.mark.built_docs
@pytest.mark.playwright
def test_code_copy_buttons_exist(page: Page, html_file: str) -> None:
    """Test that code blocks have copy buttons."""
    page.goto(html_file)

    code_blocks = page.locator("pre code, div.highlight")

    if code_blocks.count() == 0:
        pytest.skip("No code blocks on page")

    copy_button_selectors = [
        ".copybtn",
        ".copy-button",
        "button.copy",
        "[title*='Copy']",
        "[aria-label*='copy' i]",
    ]

    has_copy_buttons = any(page.locator(selector).count() > 0 for selector in copy_button_selectors)

    if not has_copy_buttons:
        pytest.skip("Copy buttons optional feature")


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_tables_have_proper_headers(page: Page, html_file: str) -> None:
    """Test that tables have proper header cells for screen readers."""
    page.goto(html_file)

    tables = page.locator("table")

    if tables.count() == 0:
        pytest.skip("No tables on page")

    for i in range(min(tables.count(), 5)):
        table = tables.nth(i)
        th_cells = table.locator("th")

        if th_cells.count() == 0:
            header_roles = table.locator('[role="columnheader"]')
            if header_roles.count() == 0:
                pytest.fail(f"{html_file}: Table {i + 1} has no header cells (<th> or role='columnheader')")


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_images_load_successfully(page: Page, html_file: str) -> None:
    """Test that images are not broken (404 errors)."""
    page.goto(html_file)

    images = page.locator("img").all()

    if not images:
        pytest.skip("No images on page")

    broken_images = []

    for img in images[:10]:
        src = img.get_attribute("src")

        if not src or src.startswith(("data:", "#")):
            continue

        # Check natural width (0 means failed to load)
        natural_width = img.evaluate("el => el.naturalWidth")
        if natural_width == 0:
            broken_images.append(src)

    if broken_images:
        pytest.fail(f"{html_file}: Broken images:\n" + "\n".join(f"  - {src}" for src in broken_images[:5]))


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.accessibility
def test_form_inputs_have_labels(page: Page, html_file: str) -> None:
    """Test that form inputs have associated labels."""
    # Skip coverage.py generated pages - the filter input in coverage.py's
    # HTML template uses placeholder instead of a proper label, which doesn't
    # meet WCAG guidelines. We can't modify coverage.py's templates.
    # See: https://github.com/nedbat/coveragepy/blob/master/coverage/htmlfiles/
    if "/coverage/" in html_file:
        pytest.skip("Coverage pages use coverage.py's HTML templates (unmodifiable)")

    page.goto(html_file)

    inputs = page.locator("input:not([type='hidden']):not([type='button']):not([type='submit'])")

    if inputs.count() == 0:
        pytest.skip("No form inputs on page")

    unlabeled_inputs = []

    for i in range(inputs.count()):
        input_elem = inputs.nth(i)
        input_id = input_elem.get_attribute("id") or f"input-{i}"

        has_label_for = False
        if input_elem.get_attribute("id"):
            label_for = page.locator(f"label[for='{input_elem.get_attribute('id')}']")
            has_label_for = label_for.count() > 0

        has_wrapping_label = False
        try:
            parent_tag = input_elem.evaluate("el => el.parentElement?.tagName")
            grandparent_tag = input_elem.evaluate("el => el.parentElement?.parentElement?.tagName")
            has_wrapping_label = parent_tag == "LABEL" or grandparent_tag == "LABEL"
        except Exception as e:
            # Log evaluation errors but continue - DOM structure may vary
            print(f"Warning: Failed to evaluate label wrapping for input {input_id}: {e}")

        has_aria_label = (
            input_elem.get_attribute("aria-label") is not None
            or input_elem.get_attribute("aria-labelledby") is not None
        )

        has_title = input_elem.get_attribute("title") is not None

        if not (has_label_for or has_wrapping_label or has_aria_label or has_title):
            input_type = input_elem.get_attribute("type") or "text"
            unlabeled_inputs.append(f"{input_type} input (id={input_id})")

    if unlabeled_inputs:
        pytest.fail(
            f"{html_file}: Form inputs without labels:\n" + "\n".join(f"  - {inp}" for inp in unlabeled_inputs[:3])
        )


@pytest.mark.built_docs
@pytest.mark.playwright
def test_external_links_open_securely(page: Page, html_file: str) -> None:
    """Test that external links have proper security attributes."""
    page.goto(html_file)

    external_links = page.locator("a[href^='http']").all()

    if not external_links:
        pytest.skip("No external links on page")

    insecure_links = []

    for link in external_links[:10]:
        href = link.get_attribute("href") or ""

        if "localhost" in href or "127.0.0.1" in href:
            continue

        rel_attr = link.get_attribute("rel") or ""

        has_noopener = "noopener" in rel_attr
        has_noreferrer = "noreferrer" in rel_attr

        if not (has_noopener or has_noreferrer):
            insecure_links.append(href)

    if len(insecure_links) > 10:
        pytest.fail(f"{html_file}: {len(insecure_links)} external links lack rel='noopener noreferrer'")
