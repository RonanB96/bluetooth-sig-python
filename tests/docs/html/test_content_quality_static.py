"""Test content quality using HTML parsing.

These tests validate Sphinx-generated content like version information
and documentation structure.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from bs4 import BeautifulSoup


@pytest.mark.built_docs
def test_documentation_includes_version_information(index_html_path: Path) -> None:
    """Test that documentation includes version information (added by Sphinx)."""
    with open(index_html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    page_text = soup.get_text().lower()

    # Check for version indicators
    version_indicators = [
        "version",
        "v0.",
        "v1.",
        "release",
        "latest",
    ]

    has_version = any(indicator in page_text for indicator in version_indicators)

    if not has_version:
        pytest.skip("Version information not found (optional but recommended)")


@pytest.mark.built_docs
def test_documentation_has_diataxis_structure(index_html_path: Path) -> None:
    """Test that main documentation follows Diataxis framework structure."""
    with open(index_html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    content = soup.get_text().lower()

    # Check for Diataxis sections
    diataxis_sections = {
        "tutorials": ["tutorial", "getting started", "quick start"],
        "how-to": ["how-to", "how to", "guide"],
        "reference": ["reference", "api"],
        "explanation": ["explanation", "understanding", "concepts"],
    }

    found_sections: list[str] = []
    for section_name, keywords in diataxis_sections.items():
        if any(keyword in content for keyword in keywords):
            found_sections.append(section_name)

    # Diataxis requires all four quadrants
    missing_sections: list[str] = []
    for section in diataxis_sections:
        if section not in found_sections:
            missing_sections.append(section)

    if missing_sections:
        pytest.fail(
            f"Documentation missing Diataxis sections: {', '.join(missing_sections)}. "
            f"Found: {', '.join(found_sections) if found_sections else 'none'}"
        )


@pytest.mark.built_docs
def test_api_documentation_exists(docs_build_dir: Path) -> None:
    """Test that API documentation was generated."""
    api_dir = docs_build_dir / "api"

    if not api_dir.exists():
        pytest.fail("API documentation directory not found")

    # Check for at least some API HTML files
    api_files = list(api_dir.rglob("*.html"))

    if not api_files:
        pytest.fail("No API documentation HTML files found")

    # Verify at least one file has actual API content
    has_api_content = False
    for api_file in api_files[:5]:  # Check first 5 files
        with open(api_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Look for typical API documentation elements
        content = soup.get_text().lower()
        if any(
            keyword in content
            for keyword in ["class", "function", "method", "parameter", "returns", "attributes", "module"]
        ):
            has_api_content = True
            break

    if not has_api_content:
        pytest.fail("API documentation files exist but appear to lack API content")
