"""Test to ensure all characteristics have individual test files."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from bluetooth_sig.gatt.characteristics import BaseCharacteristic

# Modules that contain utility/base code, not individual characteristics.
_EXCLUDED_MODULES = frozenset(
    {
        "base",
        "blood_pressure_common",
        "characteristic_meta",
        "context_lookup",
        "custom",
        "descriptor_mixin",
        "device_info",
        "fitness_machine_common",
        "role_classifier",
        "unknown",
        "utils",
    }
)

# Test files that don't correspond to individual characteristics.
_EXCLUDED_TEST_FILES = frozenset(
    {
        "test_base_characteristic.py",
        "test_characteristic_common.py",
        "test_characteristic_role.py",
        "test_characteristic_test_coverage.py",
        "test_custom_characteristics.py",
        "test_python_type_auto_resolution.py",
        "test_templates.py",
        "test_vendor_parsers.py",
    }
)


def _discover_all_characteristic_classes() -> dict[str, str]:
    """Discover all characteristic classes by scanning module files.

    Returns a dict of module_stem → class name. This avoids relying on
    ``__init__.py`` re-exports, which may lag behind new modules.
    """
    char_pkg_dir = (
        Path(importlib.util.find_spec("bluetooth_sig.gatt.characteristics").origin).parent  # type: ignore[union-attr, arg-type]
    )
    class_by_module: dict[str, str] = {}
    for py_file in sorted(char_pkg_dir.glob("*.py")):
        stem = py_file.stem
        if stem.startswith("_") or stem in _EXCLUDED_MODULES:
            continue
        module_name = f"bluetooth_sig.gatt.characteristics.{stem}"
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            continue
        for _name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, BaseCharacteristic) and obj is not BaseCharacteristic and obj.__module__ == module_name:
                class_by_module[stem] = obj.__name__
    return class_by_module


class TestCharacteristicTestFileCoverage:
    """Test that all characteristics have individual test files."""

    def test_characteristic_test_coverage(self) -> None:
        """Test that every characteristic class has a corresponding test file and vice versa."""
        class_by_module = _discover_all_characteristic_classes()

        # Collect test file stems → module stem (test_foo.py → foo)
        test_dir = Path(__file__).parent
        test_modules: dict[str, str] = {}
        for test_file in test_dir.glob("test_*.py"):
            if test_file.name not in _EXCLUDED_TEST_FILES:
                stem = test_file.stem.removeprefix("test_")
                test_modules[stem] = test_file.name

        # Compare using module stems directly
        missing_modules = set(class_by_module) - set(test_modules)
        extra_modules = set(test_modules) - set(class_by_module)

        missing_tests = sorted(class_by_module[k] for k in missing_modules)
        extra_tests = sorted(test_modules[k] for k in extra_modules)

        issues: list[str] = []
        if missing_tests:
            issues.append(
                f"Missing individual test files for {len(missing_tests)} characteristics: "
                f"{missing_tests}. Each characteristic should have a dedicated "
                f"test file (e.g., test_battery_level.py for BatteryLevelCharacteristic)."
            )
        if extra_tests:
            issues.append(
                f"Found {len(extra_tests)} test files that don't correspond to existing "
                f"characteristics: {extra_tests}. These test files should be removed "
                f"or the corresponding characteristics should be added."
            )

        assert not issues, "\n\n".join(issues)
