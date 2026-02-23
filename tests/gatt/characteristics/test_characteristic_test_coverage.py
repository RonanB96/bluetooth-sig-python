"""Test to ensure all characteristics have individual test files."""

from __future__ import annotations

import inspect
from pathlib import Path

import bluetooth_sig.gatt.characteristics as char_module
from bluetooth_sig.gatt.characteristics import BaseCharacteristic
from bluetooth_sig.gatt.resolver import NameNormalizer


class TestCharacteristicTestFileCoverage:
    """Test that all characteristics have individual test files."""

    def test_characteristic_test_coverage(self) -> None:
        """Test that every characteristic class has a corresponding test file and vice versa.

        This ensures that each characteristic implementation has dedicated
        tests for its specific functionality, and that we don't have orphaned test files.
        """
        # Get all characteristic classes
        all_characteristic_classes = set()
        for _name, obj in inspect.getmembers(char_module):
            if inspect.isclass(obj) and issubclass(obj, BaseCharacteristic) and obj is not BaseCharacteristic:
                all_characteristic_classes.add(obj)

        # Get all test files in this directory
        test_dir = Path(__file__).parent
        test_files = set()
        # Test files that don't correspond to individual characteristics
        excluded_test_files = {
            "test_base_characteristic.py",  # Tests base class
            "test_characteristic_common.py",  # Common test utilities
            "test_characteristic_role.py",  # Tests role classification, not a single characteristic
            "test_characteristic_test_coverage.py",  # This coverage test
            "test_custom_characteristics.py",  # Tests custom characteristic functionality
            "test_python_type_auto_resolution.py",  # Tests python_type auto-resolution mechanism
            "test_templates.py",  # Tests template classes, not characteristics
        }
        for test_file in test_dir.glob("test_*.py"):
            if test_file.name not in excluded_test_files:
                test_name = test_file.stem.replace("test_", "")
                camel_case = NameNormalizer.snake_case_to_camel_case(test_name)
                test_files.add(camel_case + "Characteristic")

        # Check for missing test files
        missing_tests = []
        for cls in all_characteristic_classes:
            expected_test_name = cls.__name__
            if expected_test_name not in test_files:
                missing_tests.append(expected_test_name)

        # Check for extra test files
        characteristic_names = {cls.__name__ for cls in all_characteristic_classes}
        extra_tests = test_files - characteristic_names

        # Report issues
        issues = []
        if missing_tests:
            issues.append(
                f"Missing individual test files for {len(missing_tests)} characteristics: "
                f"{sorted(missing_tests)}. Each characteristic should have a dedicated "
                f"test file (e.g., test_battery_level.py for BatteryLevelCharacteristic)."
            )
        if extra_tests:
            issues.append(
                f"Found {len(extra_tests)} test files that don't correspond to existing "
                f"characteristics: {sorted(extra_tests)}. These test files should be removed "
                f"or the corresponding characteristics should be added."
            )

        # Assert no issues
        assert not issues, "\n\n".join(issues)
