"""Test to ensure all services have individual test files."""

from __future__ import annotations

import inspect
from pathlib import Path

import bluetooth_sig.gatt.services as svc_module
from bluetooth_sig.gatt.resolver import NameNormalizer
from bluetooth_sig.gatt.services.base import BaseGattService


class TestServiceTestFileCoverage:
    """Test that all services have individual test files."""

    def test_service_test_coverage(self) -> None:
        """Test that every service class has a corresponding test file and vice versa.

        This ensures that each service implementation has dedicated
        tests for its specific functionality, and that we don't have orphaned test files.
        """
        # Get all service classes
        all_service_classes = set()
        for _name, obj in inspect.getmembers(svc_module):
            if inspect.isclass(obj) and issubclass(obj, BaseGattService) and obj is not BaseGattService:
                all_service_classes.add(obj)

        # Get all test files in this directory
        test_dir = Path(__file__).parent
        test_files = set()
        # Test files that don't correspond to individual services
        excluded_test_files = {
            "test_service_common.py",  # Common test utilities
            "test_service_coverage.py",  # This coverage test
            "test_custom_services.py",  # Tests custom service functionality
        }
        for test_file in test_dir.glob("test_*.py"):
            if test_file.name not in excluded_test_files:
                test_name = test_file.stem.replace("test_", "").replace("_service", "")
                camel_case = NameNormalizer.snake_case_to_camel_case(test_name)
                # Special case for automation_io -> AutomationIO
                if test_name == "automation_io":
                    camel_case = "AutomationIO"
                test_files.add(camel_case + "Service")

        # Check for missing test files
        missing_tests = []
        for cls in all_service_classes:
            expected_test_name = cls.__name__
            if expected_test_name not in test_files:
                missing_tests.append(expected_test_name)

        # Check for extra test files
        service_names = {cls.__name__ for cls in all_service_classes}
        extra_tests = test_files - service_names

        # Report issues
        issues = []
        if missing_tests:
            issues.append(
                f"Missing individual test files for {len(missing_tests)} services: "
                f"{sorted(missing_tests)}. Each service should have a dedicated "
                f"test file (e.g., test_battery_service.py for BatteryService)."
            )
        if extra_tests:
            issues.append(
                f"Found {len(extra_tests)} test files that don't correspond to existing "
                f"services: {sorted(extra_tests)}. These test files should be removed "
                f"or the corresponding services should be added."
            )

        # Assert no issues
        assert not issues, "\n\n".join(issues)
