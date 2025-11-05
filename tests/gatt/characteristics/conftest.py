"""Pytest configuration for characteristic tests.

This conftest implements collection hooks to optimize test discovery
and eliminate unnecessary skipped tests.
"""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(
    session: pytest.Session,
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Remove dependency tests for characteristics without dependencies.

    Background:
    - CommonCharacteristicTests base class has 4 dependency test methods
    - These tests are inherited by all 91 characteristic test classes
    - Only some characteristics actually have dependencies
    - Without filtering, hundreds of unnecessary tests are collected and skipped

    This hook:
    1. Automatically detects which test classes override dependency_test_data fixture
    2. Removes dependency tests from classes without dependency data
    3. Shows removed tests as "deselected" (like -k filter) not "skipped"

    Result: Clean test output without hundreds of skipped tests cluttering results.

    Scalability: Automatically adapts when new characteristics with dependencies are added.
    Just override dependency_test_data fixture in your test class and return test data.
    """
    selected = []
    deselected = []

    # First pass: identify which test classes override dependency_test_data fixture
    # by checking if the method is defined in the test class (not inherited from base)
    classes_with_dependency_data: set[tuple[str, str]] = set()

    for item in items:
        # Only check dependency test items (optimization)
        if not item.name.startswith("test_dependency_"):
            continue

        # Get the test class
        test_class = item.parent
        if test_class is None or not isinstance(test_class, pytest.Class):
            continue

        # Check if the test class defines its own dependency_test_data method
        # (not inherited from CommonCharacteristicTests)
        if hasattr(test_class.cls, "dependency_test_data"):
            # Check if dependency_test_data is defined in this specific class
            # by checking if it exists in the class's __dict__ (not inherited)
            if "dependency_test_data" in test_class.cls.__dict__:
                # This class overrides the fixture - it has dependency data
                class_name = test_class.cls.__name__
                test_file = item.path.name if hasattr(item, "path") else item.fspath.basename
                classes_with_dependency_data.add((test_file, class_name))

    # Second pass: filter out dependency tests from classes without dependency data
    for item in items:
        # Check if this is a dependency test method
        if item.name.startswith("test_dependency_"):
            # Get the test class info
            test_class = item.parent
            if test_class is not None and isinstance(test_class, pytest.Class):
                class_name = test_class.cls.__name__
                test_file = item.path.name if hasattr(item, "path") else item.fspath.basename

                # If this class doesn't override dependency_test_data, deselect the test
                if classes_with_dependency_data and (test_file, class_name) not in classes_with_dependency_data:
                    deselected.append(item)
                    continue

        # Keep all non-dependency tests and dependency tests from classes with dependencies
        selected.append(item)

    # Apply deselection if any tests were removed
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
