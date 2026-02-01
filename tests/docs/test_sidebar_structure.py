"""Test sidebar content structure using HTML parsing.

This test validates the sidebar navigation items to prevent regressions
in the documentation structure. The sidebar frequently breaks during
documentation updates, so these tests ensure critical navigation
elements remain present and correctly structured.

These tests use Python's built-in HTML parser and don't require Playwright,
making them faster and easier to run in CI/CD pipelines.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from tests.docs.conftest import (
    CSS_CLASS_SIDEBAR_BRAND,
    CSS_CLASS_SIDEBAR_DRAWER,
    CSS_CLASS_SIDEBAR_SEARCH,
    CSS_CLASS_SIDEBAR_TREE,
    CSS_CLASS_TOCTREE_CHECKBOX,
    CSS_CLASS_TOCTREE_L1,
    EXPECTED_SECTION_ORDER,
    REQUIRED_SECTIONS,
)


class SidebarParser(HTMLParser):  # pylint: disable=too-many-instance-attributes
    """HTML parser to extract sidebar navigation structure."""

    def __init__(self) -> None:
        """Initialize the parser with empty state tracking."""
        super().__init__()
        self.in_sidebar_tree = False
        self.in_toctree_l1 = False
        self.in_link = False
        self.current_link_text = ""
        self.current_link_href = ""
        self.sidebar_sections: list[tuple[str, str]] = []
        self.has_sidebar_brand = False
        self.has_sidebar_search = False
        self.sidebar_brand_text = ""
        self.in_brand = False

    def error(self, message: str) -> None:
        """Handle parsing errors."""
        # HTMLParser requires this method but we don't need custom error handling

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Process opening HTML tags."""
        attrs_dict = dict(attrs)

        # Track sidebar tree
        if attrs_dict.get("class"):
            classes = attrs_dict["class"].split() if attrs_dict["class"] else []
            if CSS_CLASS_SIDEBAR_TREE in classes:
                self.in_sidebar_tree = True
            if CSS_CLASS_TOCTREE_L1 in classes and self.in_sidebar_tree:
                self.in_toctree_l1 = True
            if CSS_CLASS_SIDEBAR_BRAND in classes:
                self.in_brand = True
                self.has_sidebar_brand = True
            if CSS_CLASS_SIDEBAR_SEARCH in classes:
                self.has_sidebar_search = True

        # Track links in top-level navigation
        if tag == "a" and self.in_toctree_l1:
            href = attrs_dict.get("href", "")
            if "class" in attrs_dict and "reference" in (attrs_dict["class"] or ""):
                self.in_link = True
                self.current_link_href = href or ""

    def handle_endtag(self, tag: str) -> None:
        """Process closing HTML tags."""
        if tag == "a" and self.in_link:
            if self.current_link_text and self.current_link_href:
                self.sidebar_sections.append((self.current_link_text.strip(), self.current_link_href))
            self.in_link = False
            self.current_link_text = ""
            self.current_link_href = ""
        elif tag == "li" and self.in_toctree_l1:
            self.in_toctree_l1 = False
        elif tag == "div":
            # Check if we're leaving sidebar-tree
            self.in_sidebar_tree = False
        elif tag == "a" and self.in_brand:
            self.in_brand = False

    def handle_data(self, data: str) -> None:
        """Process text content."""
        if self.in_link:
            self.current_link_text += data
        elif self.in_brand:
            self.sidebar_brand_text += data


def get_index_html_path() -> Path:
    """Get the path to the built documentation index.html."""
    # Start from test file location
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    index_path = project_root / "docs" / "build" / "html" / "index.html"
    return index_path


@pytest.mark.built_docs
def test_sidebar_html_has_required_sections() -> None:
    """Test that sidebar contains all required top-level navigation sections.

    These sections follow the Diátaxis framework and are critical for
    documentation navigation. Any missing section indicates a broken build.
    """
    index_path = get_index_html_path()

    if not index_path.exists():
        pytest.skip(f"Documentation not built: {index_path}")

    # Parse the HTML
    parser = SidebarParser()
    with open(index_path, encoding="utf-8") as f:
        parser.feed(f.read())

    # Check each required section
    found_sections = dict(parser.sidebar_sections)
    missing_sections: list[str] = []
    incorrect_hrefs: list[str] = []

    for section_name, expected_href in REQUIRED_SECTIONS.items():
        if section_name not in found_sections:
            missing_sections.append(section_name)
        else:
            actual_href = found_sections[section_name]
            if expected_href not in actual_href:
                incorrect_hrefs.append(f"{section_name}: expected '{expected_href}', got '{actual_href}'")

    errors: list[str] = []
    if missing_sections:
        errors.append(
            "Missing required sidebar sections:\n" + "\n".join(f"  - {section}" for section in missing_sections)
        )
    if incorrect_hrefs:
        errors.append("Incorrect section hrefs:\n" + "\n".join(f"  - {error}" for error in incorrect_hrefs))

    if errors:
        pytest.fail("\n\n".join(errors))


@pytest.mark.built_docs
def test_sidebar_sections_maintain_order() -> None:
    """Test that sidebar sections appear in the correct order.

    The order of sections is important for documentation flow.
    This test ensures sections aren't accidentally reordered.
    """
    index_path = get_index_html_path()

    if not index_path.exists():
        pytest.skip(f"Documentation not built: {index_path}")

    # Parse the HTML
    parser = SidebarParser()
    with open(index_path, encoding="utf-8") as f:
        parser.feed(f.read())

    # Get actual order from parsed sections
    actual_order = [text for text, _ in parser.sidebar_sections]

    # Filter to only the expected sections
    actual_filtered = [s for s in actual_order if s in EXPECTED_SECTION_ORDER]
    expected_filtered = [s for s in EXPECTED_SECTION_ORDER if s in actual_filtered]

    assert actual_filtered == expected_filtered, (
        f"Sidebar sections are in wrong order.\nExpected: {expected_filtered}\nActual:   {actual_filtered}"
    )


@pytest.mark.built_docs
def test_sidebar_has_brand() -> None:
    """Test that sidebar displays correct project branding.

    Ensures the project name and version are correctly displayed
    in the sidebar header.
    """
    index_path = get_index_html_path()

    if not index_path.exists():
        pytest.skip(f"Documentation not built: {index_path}")

    # Parse the HTML
    parser = SidebarParser()
    with open(index_path, encoding="utf-8") as f:
        parser.feed(f.read())

    assert parser.has_sidebar_brand, "Sidebar brand element not found"

    brand_text = parser.sidebar_brand_text.strip()

    # Should contain project name
    assert "Bluetooth SIG Standards Library" in brand_text, f"Sidebar brand missing project name. Found: '{brand_text}'"

    # Should contain version or "documentation"
    assert any(keyword in brand_text for keyword in ["documentation", "0.", "1."]), (
        f"Sidebar brand missing version or 'documentation'. Found: '{brand_text}'"
    )


@pytest.mark.built_docs
def test_sidebar_has_search() -> None:
    """Test that sidebar has search functionality.

    Ensures the search box is present in the sidebar.
    """
    index_path = get_index_html_path()

    if not index_path.exists():
        pytest.skip(f"Documentation not built: {index_path}")

    # Parse the HTML
    parser = SidebarParser()
    with open(index_path, encoding="utf-8") as f:
        parser.feed(f.read())

    assert parser.has_sidebar_search, "Sidebar search element not found"


@pytest.mark.built_docs
def test_sidebar_structure_in_html() -> None:
    """Test that sidebar HTML structure is well-formed.

    Validates the overall sidebar DOM structure using regex patterns
    to catch malformed HTML that could break navigation rendering.
    """
    index_path = get_index_html_path()

    if not index_path.exists():
        pytest.skip(f"Documentation not built: {index_path}")

    with open(index_path, encoding="utf-8") as f:
        html_content = f.read()

    # Check for critical sidebar structure elements
    required_patterns = [
        (rf'class="{CSS_CLASS_SIDEBAR_DRAWER}"', f"Sidebar container (.{CSS_CLASS_SIDEBAR_DRAWER})"),
        (rf'class="{CSS_CLASS_SIDEBAR_BRAND}"', "Sidebar brand"),
        (rf'class="{CSS_CLASS_SIDEBAR_SEARCH}"', "Sidebar search"),
        (rf'class="{CSS_CLASS_SIDEBAR_TREE}"', f"Sidebar tree (.{CSS_CLASS_SIDEBAR_TREE})"),
        (rf'class="{CSS_CLASS_TOCTREE_L1}', "Top-level navigation items"),
    ]

    missing_elements: list[str] = []

    for pattern, description in required_patterns:
        if not re.search(pattern, html_content):
            missing_elements.append(description)

    if missing_elements:
        pytest.fail(
            "Missing required sidebar structure elements:\n" + "\n".join(f"  - {elem}" for elem in missing_elements)
        )


@pytest.mark.built_docs
def test_sidebar_navigation_links_are_well_formed() -> None:
    """Test that sidebar navigation links have valid structure.

    Ensures that all navigation links have proper href attributes
    and non-empty text content.
    """
    index_path = get_index_html_path()

    if not index_path.exists():
        pytest.skip(f"Documentation not built: {index_path}")

    # Parse the HTML
    parser = SidebarParser()
    with open(index_path, encoding="utf-8") as f:
        parser.feed(f.read())

    assert len(parser.sidebar_sections) > 0, "No sidebar sections found"

    malformed_links: list[str] = []

    for text, href in parser.sidebar_sections:
        if not text:
            malformed_links.append(f"Empty text with href='{href}'")
        if not href:
            malformed_links.append(f"Empty href for text='{text}'")

    if malformed_links:
        pytest.fail("Malformed sidebar links found:\n" + "\n".join(f"  - {link}" for link in malformed_links))


@pytest.mark.built_docs
def test_sidebar_has_expandable_sections() -> None:
    """Test that sidebar has expandable navigation sections.

    Ensures that the HTML contains the checkbox pattern used for
    expanding/collapsing navigation sections.
    """
    index_path = get_index_html_path()

    if not index_path.exists():
        pytest.skip(f"Documentation not built: {index_path}")

    with open(index_path, encoding="utf-8") as f:
        html_content = f.read()

    # Check for toctree checkboxes (used for expand/collapse)
    checkbox_pattern = rf'class="{CSS_CLASS_TOCTREE_CHECKBOX}"'
    checkboxes = re.findall(checkbox_pattern, html_content)

    assert len(checkboxes) > 0, "No expandable sections found (missing .toctree-checkbox elements)"

    # Check that checkboxes have ARIA labels
    aria_label_pattern = r'aria-label="Toggle navigation'
    aria_labels = re.findall(aria_label_pattern, html_content)

    assert len(aria_labels) > 0, "Expandable sections missing ARIA labels for accessibility"
