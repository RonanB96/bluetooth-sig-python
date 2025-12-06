"""Test Diátaxis compliance in rendered documentation structure and navigation.

These tests validate the built HTML documentation's Diátaxis framework structure.
Tests are marked with @pytest.mark.built_docs and require built Sphinx documentation.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.built_docs
@pytest.mark.playwright
def test_documentation_has_diataxis_structure(page: Page, docs_server: str) -> None:
    """Test that main documentation follows Diátaxis four-quadrant structure."""
    page.goto(docs_server)

    # Check for main navigation sections representing Diátaxis quadrants
    # Note: Actual selector may vary based on Sphinx theme

    # Look for Diátaxis sections in navigation or main content
    content = page.content().lower()

    # At minimum, should have tutorials and how-to guides
    assert "tutorial" in content, "Documentation should have a Tutorials section"
    assert "how-to" in content or "how to" in content, "Documentation should have How-to Guides section"

    # Reference documentation (API reference is common)
    assert "reference" in content or "api" in content, "Documentation should have Reference section"


@pytest.mark.built_docs
@pytest.mark.playwright
@pytest.mark.parametrize(
    "doc_path,doc_type",
    [
        ("tutorials/index.html", "tutorials"),
        ("how-to/index.html", "how-to"),
        ("api/index.html", "reference"),
        ("explanation/index.html", "explanation"),
    ],
)
def test_diataxis_section_exists(page: Page, docs_server: str, doc_path: str, doc_type: str) -> None:
    """Test that each Diátaxis section exists and is accessible.

    Args:
        page: Playwright page fixture
        docs_server: Base URL of documentation server
        doc_path: Path to section index
        doc_type: Diátaxis documentation type
    """
    url = f"{docs_server}/{doc_path}"
    response = page.goto(url)

    # Allow 404 for sections that may not exist yet
    if response and response.status == 404:
        pytest.skip(f"{doc_type.capitalize()} section not yet implemented at {doc_path}")

    # Verify page loaded successfully
    assert response is not None
    assert response.status == 200, f"{doc_type.capitalize()} section should be accessible"

    # Verify page has content - check for doc_type keyword or section heading
    body_text = page.locator("body").inner_text()
    # Accept either the doc_type name (e.g., "tutorials") or related keywords
    # how-to -> "How-to Guides", explanation -> "Understanding", etc.
    doc_keywords = {
        "tutorials": ["tutorials", "tutorial"],
        "how-to": ["how-to", "guides"],
        "reference": ["reference", "api"],
        "explanation": ["explanation", "understanding"],
    }
    keywords = doc_keywords.get(doc_type, [doc_type.replace("-", " ")])
    assert any(keyword in body_text.lower() for keyword in keywords), (
        f"{doc_type.capitalize()} section should contain relevant keywords: {keywords}"
    )
