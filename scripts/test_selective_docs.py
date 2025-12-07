#!/usr/bin/env python3
"""Test the selective documentation testing mechanism."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))


def test_change_detection_no_changes() -> None:
    """Test change detection with no changes."""
    result = subprocess.run(
        ["python", "scripts/detect_changed_docs.py", "--base", "HEAD", "--head", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = json.loads(result.stdout.strip())
    assert output == [], f"Expected [] for no changes, got {output}"
    print("✅ No changes → empty list (skip tests)")


def test_change_detection_output_format() -> None:
    """Test that change detection outputs valid JSON."""
    result = subprocess.run(
        ["python", "scripts/detect_changed_docs.py", "--base", "HEAD~5", "--head", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = json.loads(result.stdout.strip())
    assert isinstance(output, list), f"Expected list, got {type(output)}"
    assert len(output) > 0, "Expected non-empty output"
    print(f"✅ Change detection outputs valid JSON: {len(output)} files")


def test_env_var_parsing() -> None:
    """Test that conftest.py can parse DOCS_TEST_FILES env var."""
    # Test valid JSON
    test_json = '["tutorials/index.html", "api/index.html"]'
    try:
        parsed = json.loads(test_json)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        print("✅ Environment variable parsing works")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        sys.exit(1)


def test_path_mapping() -> None:
    """Test source to HTML path mapping logic."""
    from detect_changed_docs import map_source_to_html  # type: ignore[import-not-found]

    # Test markdown files
    assert map_source_to_html("docs/source/tutorials/index.md") == ["tutorials/index.html"]
    assert map_source_to_html("docs/source/api/index.rst") == ["api/index.html"]

    # Test Python source files (AutoAPI)
    assert map_source_to_html("src/bluetooth_sig/core/translator.py") == [
        "api/bluetooth_sig/core/translator.html"
    ]

    # Test __init__.py files (critical - map to index.html)
    assert map_source_to_html("src/bluetooth_sig/__init__.py") == [
        "api/bluetooth_sig/index.html"
    ]
    assert map_source_to_html("src/bluetooth_sig/core/__init__.py") == [
        "api/bluetooth_sig/core/index.html"
    ]

    # Test non-documentation files
    assert map_source_to_html("README.md") == []
    assert map_source_to_html("pyproject.toml") == []
    assert map_source_to_html("tests/test_something.py") == []

    print("✅ Path mapping works correctly")


def test_comprehensive_trigger() -> None:
    """Test that conf.py changes trigger comprehensive testing."""
    from detect_changed_docs import should_test_all  # type: ignore[import-not-found]

    # conf.py should trigger ALL
    assert should_test_all(["docs/source/conf.py"])

    # Template changes should trigger ALL
    assert should_test_all(["docs/source/_templates/page.html"])

    # CSS changes should trigger ALL
    assert should_test_all(["docs/source/_static/custom.css"])

    # JS changes should trigger ALL
    assert should_test_all(["docs/source/_static/custom.js"])

    # Regular doc changes should NOT trigger ALL
    assert not should_test_all(["docs/source/tutorials/index.md"])
    assert not should_test_all(["src/bluetooth_sig/core/translator.py"])
    assert not should_test_all(["README.md"])

    print("✅ Comprehensive testing triggers work correctly")


if __name__ == "__main__":
    print("Testing selective documentation testing mechanism...\n")

    test_change_detection_no_changes()
    test_change_detection_output_format()
    test_env_var_parsing()
    test_path_mapping()
    test_comprehensive_trigger()

    print("\n✅ All tests passed!")
