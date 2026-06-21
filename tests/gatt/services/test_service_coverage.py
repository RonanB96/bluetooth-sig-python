"""Test to ensure all services have individual test files."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from bluetooth_sig.gatt.resolver import NameNormalizer

_EXCLUDED_SERVICE_MODULES = frozenset(
    {
        "__init__",
        "_export_map",
        "base",
        "custom",
        "registry",
        "unknown",
    }
)

# Services implemented before dedicated test coverage was enforced for every module.
_COVERAGE_DEFERRED_SERVICES = frozenset(
    {
        "FitnessMachineService",
        "HumanInterfaceDeviceService",
        "PulseOximeterService",
        "UserDataService",
    }
)


def _module_stem_to_service_name(stem: str) -> str:
    service_stem = stem.removesuffix("_service")
    camel_case = NameNormalizer.snake_case_to_camel_case(service_stem)
    if service_stem == "automation_io":
        camel_case = "AutomationIO"
    return f"{camel_case}Service"


def _discover_service_class_names() -> set[str]:
    """Discover service class names by scanning module files."""
    svc_pkg_dir = Path(importlib.util.find_spec("bluetooth_sig.gatt.services").origin).parent  # type: ignore[union-attr, arg-type]
    return {
        _module_stem_to_service_name(module_path.stem)
        for module_path in svc_pkg_dir.glob("*.py")
        if module_path.stem not in _EXCLUDED_SERVICE_MODULES
    }


class TestServiceTestFileCoverage:
    """Test that all services have individual test files."""

    def test_service_test_coverage(self) -> None:
        """Test that every service class has a corresponding test file and vice versa."""
        all_service_classes = _discover_service_class_names() - _COVERAGE_DEFERRED_SERVICES

        test_dir = Path(__file__).parent
        test_files: set[str] = set()
        excluded_test_files = {
            "test_service_common.py",
            "test_service_coverage.py",
            "test_custom_services.py",
        }
        for test_file in test_dir.glob("test_*.py"):
            if test_file.name not in excluded_test_files:
                test_name = test_file.stem.replace("test_", "").replace("_service", "")
                camel_case = NameNormalizer.snake_case_to_camel_case(test_name)
                if test_name == "automation_io":
                    camel_case = "AutomationIO"
                test_files.add(f"{camel_case}Service")

        missing_tests = sorted(all_service_classes - test_files)
        extra_tests = sorted(test_files - all_service_classes)

        issues: list[str] = []
        if missing_tests:
            issues.append(
                f"Missing individual test files for {len(missing_tests)} services: "
                f"{missing_tests}. Each service should have a dedicated "
                f"test file (e.g., test_battery_service.py for BatteryService)."
            )
        if extra_tests:
            issues.append(
                f"Found {len(extra_tests)} test files that don't correspond to existing "
                f"services: {extra_tests}. These test files should be removed "
                f"or the corresponding services should be added."
            )

        assert not issues, "\n\n".join(issues)
