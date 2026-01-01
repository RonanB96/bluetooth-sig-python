"""Pytest configuration for HTML parsing tests.

These tests parse built HTML documentation without requiring a browser.
They validate static HTML structure, accessibility attributes, and theme-generated content.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.docs.conftest import DOCS_BUILD_DIR


@pytest.fixture
def html_files() -> list[Path]:
    """Get list of all HTML files to test.

    Uses DOCS_TEST_FILES environment variable to control which files are tested:
    - Not set: Test all HTML files (default)
    - Set to JSON array: Test only specified files
    - Set to '["ALL"]': Test all HTML files explicitly
    - Set to '[]': Skip all tests (no docs changed)
    """
    if not DOCS_BUILD_DIR.exists():
        pytest.skip(f"Documentation not built: {DOCS_BUILD_DIR}")

    # Check for selective testing via environment variable
    docs_test_files = os.environ.get("DOCS_TEST_FILES")

    if docs_test_files is not None:
        try:
            files_to_test = json.loads(docs_test_files)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid DOCS_TEST_FILES JSON: {docs_test_files}")

        if not files_to_test:
            pytest.skip("No documentation files to test (DOCS_TEST_FILES is empty)")

        if files_to_test == ["ALL"]:
            return list(DOCS_BUILD_DIR.rglob("*.html"))

        # Convert relative paths to absolute
        return [DOCS_BUILD_DIR / f for f in files_to_test if f.endswith(".html")]

    # Default: test all HTML files
    return list(DOCS_BUILD_DIR.rglob("*.html"))


@pytest.fixture
def index_html_path() -> Path:
    """Get path to the main index.html file."""
    index_path = DOCS_BUILD_DIR / "index.html"
    if not index_path.exists():
        pytest.skip(f"Index file not found: {index_path}")
    return index_path
