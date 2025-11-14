"""Comprehensive test to validate all services and characteristics against
YAML.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.gatt.uuid_registry import uuid_registry
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


def discover_service_classes() -> list[type[BaseGattService]]:
    """Dynamically discover all service classes."""
    service_classes = []
    services_module = importlib.import_module("bluetooth_sig.gatt.services")

    # Get the services package path
    services_path = Path(str(services_module.__file__)).parent

    # Iterate through all Python files in the services directory
    for module_info in pkgutil.iter_modules([str(services_path)]):
        if module_info.name not in ["__init__", "base"]:
            try:
                module = importlib.import_module(f"bluetooth_sig.gatt.services.{module_info.name}")

                # Find all classes that inherit from BaseGattService
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        obj != BaseGattService
                        and issubclass(obj, BaseGattService)
                        and obj.__module__ == module.__name__
                        and not getattr(obj, "_is_base_class", False)  # Exclude base classes
                    ):
                        service_classes.append(obj)
            except ImportError as e:
                pytest.fail(f"Failed to import service module {module_info.name}: {e}")

    return service_classes


def discover_characteristic_classes() -> list[type[BaseCharacteristic]]:
    """Dynamically discover all characteristic classes."""
    characteristic_classes = []
    characteristics_module = importlib.import_module("bluetooth_sig.gatt.characteristics")

    # Get the characteristics package path
    characteristics_path = Path(str(characteristics_module.__file__)).parent

    # Iterate through all Python files in the characteristics directory
    for module_info in pkgutil.iter_modules([str(characteristics_path)]):
        if module_info.name not in ["__init__", "base"]:
            try:
                module = importlib.import_module(f"bluetooth_sig.gatt.characteristics.{module_info.name}")

                # Find all classes that inherit from BaseCharacteristic
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        obj != BaseCharacteristic
                        and issubclass(obj, BaseCharacteristic)
                        and obj.__module__ == module.__name__
                        and not getattr(obj, "_is_template", False)  # Exclude templates
                        and not getattr(obj, "_is_base_class", False)  # Exclude base classes
                    ):
                        characteristic_classes.append(obj)
            except ImportError as e:
                pytest.fail(f"Failed to import characteristic module {module_info.name}: {e}")

    return characteristic_classes


class TestCharacteristicRegistryValidation:
    """Test all characteristics against the YAML registry."""

    @pytest.fixture(scope="class")
    def characteristic_classes(self) -> list[type[BaseCharacteristic]]:
        """Get all characteristic classes."""
        return discover_characteristic_classes()

    def test_all_characteristics_discovered(self, characteristic_classes: list[type[BaseCharacteristic]]) -> None:
        """Test that characteristics were discovered."""
        assert len(characteristic_classes) > 0, "No characteristic classes were discovered"

        # Print discovered characteristics for debugging
        char_names = [cls.__name__ for cls in characteristic_classes]
        print(f"Discovered characteristics: {char_names}")

    @pytest.mark.parametrize("char_class", discover_characteristic_classes())
    def test_characteristic_uuid_resolution(self, char_class: type[BaseCharacteristic]) -> None:
        """Test that each characteristic can resolve its UUID from the
        registry.
        """
        try:
            # Create an instance to trigger UUID resolution
            char = char_class()
            uuid = char.uuid

            # Verify UUID is not empty
            assert uuid, f"Characteristic {char_class.__name__} has empty UUID"

            # Verify UUID format (should be 4 characters for 16-bit UUIDs)
            assert len(uuid.short_form) == 4, (
                f"Characteristic {char_class.__name__} UUID '{uuid}' should be 4 characters"
            )
            assert all(c in "0123456789ABCDEF" for c in uuid.short_form), (
                f"Characteristic {char_class.__name__} UUID '{uuid}' should be hexadecimal"
            )

        except ValueError as e:
            pytest.fail(f"Characteristic {char_class.__name__} failed UUID resolution: {e}")

    @pytest.fixture(autouse=True)
    def _reset_registries(self, reset_registries: None) -> None:
        """Ensure registries are reset after each test."""

    @pytest.mark.parametrize("char_class", discover_characteristic_classes())
    def test_characteristic_in_yaml_registry(self, char_class: type[BaseCharacteristic]) -> None:
        """Test that each characteristic exists in the YAML registry with
        correct information.
        """
        try:
            # Resolve UUID at class level without creating instance
            uuid = char_class._resolve_from_basic_registry_class()  # type: ignore[attr-defined]
            assert uuid is not None, f"Characteristic {char_class.__name__} could not resolve UUID"

            # Create instance for name checking
            char = char_class()
            name = char.name

            # Check if UUID exists in registry
            char_info = uuid_registry.get_characteristic_info(uuid)
            assert char_info is not None, (
                f"Characteristic UUID '{uuid}' for {char_class.__name__} not found in YAML registry"
            )

            # Verify the characteristic has a valid name
            assert char_info.name, f"Characteristic {char_class.__name__} has empty name in registry"

            # Verify the characteristic name matches expected
            assert char_info.name == name, (
                f"Characteristic {char_class.__name__} name mismatch: registry='{char_info.name}', class='{name}'"
            )

            # Verify the characteristic has a valid ID
            assert char_info.id, f"Characteristic {char_class.__name__} has empty ID in registry"
            assert char_info.id.startswith("org.bluetooth.characteristic"), (
                f"Characteristic {char_class.__name__} ID should start with 'org.bluetooth.characteristic'"
            )

        except Exception as e:
            pytest.fail(f"Characteristic {char_class.__name__} registry validation failed: {e}")

    @pytest.mark.parametrize("char_class", discover_characteristic_classes())
    def test_characteristic_properties(self, char_class: type[BaseCharacteristic]) -> None:
        """Test that each characteristic has valid properties."""
        try:
            # Use Progressive API Level 1 - SIG characteristics with no parameters
            char = char_class()

            # Verify value_type is set
            assert hasattr(char, "value_type"), f"Characteristic {char_class.__name__} should have value_type attribute"
            assert char.value_type, f"Characteristic {char_class.__name__} value_type should not be empty"

            # Verify value_type is one of the expected types
            valid_types = {"string", "int", "float", "boolean", "bytes", "dict", "various"}
            assert char.value_type.value in valid_types, (
                f"Characteristic {char_class.__name__} value_type '{char.value_type.value}' "
                f"should be one of {valid_types}"
            )

            # Verify decode_value method exists
            assert hasattr(char, "decode_value"), (
                f"Characteristic {char_class.__name__} should have decode_value method"
            )
            assert callable(char.decode_value), f"Characteristic {char_class.__name__} decode_value should be callable"

            # Verify unit property exists
            assert hasattr(char, "unit"), f"Characteristic {char_class.__name__} should have unit property"
            assert isinstance(char.unit, str), f"Characteristic {char_class.__name__} unit should be a string"

        except Exception as e:
            pytest.fail(f"Characteristic {char_class.__name__} properties validation failed: {e}")

    @pytest.mark.parametrize("char_class", discover_characteristic_classes())
    def test_characteristic_name_resolution(self, char_class: type[BaseCharacteristic]) -> None:
        """Test that each characteristic can resolve its name correctly."""
        try:
            char = char_class()
            name = char.name

            # Verify name is not empty
            assert name, f"Characteristic {char_class.__name__} has empty name"

            # Try to look up by name in registry
            char_info = uuid_registry.get_characteristic_info(name)
            assert char_info is not None, (
                f"Characteristic name '{name}' for {char_class.__name__} not found in YAML registry"
            )

        except Exception as e:
            pytest.fail(f"Characteristic {char_class.__name__} name resolution failed: {e}")


class TestRegistryConsistency:
    """Test consistency between services and characteristics."""

    def test_service_characteristic_consistency(self) -> None:
        """Test that characteristics referenced by services actually exist and
        are valid.
        """
        service_classes = discover_service_classes()
        char_classes = discover_characteristic_classes()

        # Build a map of characteristic names to classes
        char_name_to_class = {}
        for char_class in char_classes:
            try:
                char = char_class()
                char_name_to_class[char.name] = char_class
            except Exception:
                continue  # Skip characteristics that can't be instantiated

        # Check each service's expected characteristics
        for service_class in service_classes:
            try:
                service = service_class()
                expected_chars = service.get_expected_characteristics()

                for char_name, char_value in expected_chars.items():
                    # Extract characteristic class from either CharacteristicSpec or direct class reference
                    if hasattr(char_value, "char_class"):  # CharacteristicSpec
                        char_cls = char_value.char_class  # type: ignore[assignment]
                    else:  # Legacy direct class reference
                        char_cls = char_value  # type: ignore[assignment]

                    # Verify the characteristic class exists in our discovered classes
                    assert char_cls in char_classes, (
                        f"Service {service_class.__name__} references unknown characteristic class {char_cls.__name__}"
                    )

                    # Verify the characteristic name matches what the class reports
                    char_key = char_name.value if hasattr(char_name, "value") else str(char_name)
                    if char_key in char_name_to_class:
                        expected_class = char_name_to_class[char_key]
                        assert char_cls == expected_class, (
                            f"Service {service_class.__name__} characteristic name '{char_key}' "
                            f"maps to wrong class. Expected {expected_class.__name__}, "
                            f"got {char_cls.__name__}"
                        )

            except Exception as e:
                pytest.fail(f"Service-characteristic consistency check failed for {service_class.__name__}: {e}")

    def test_yaml_completeness(self) -> None:
        """Test that all discovered classes have corresponding entries in YAML
        files.
        """
        service_classes = discover_service_classes()
        char_classes = discover_characteristic_classes()

        missing_services = []
        missing_characteristics = []

        # Check services
        for service_class in service_classes:
            try:
                service = service_class()
                service_uuid = service.uuid
                service_info = uuid_registry.get_service_info(service_uuid)
                if service_info is None:
                    missing_services.append(f"{service_class.__name__} (UUID: {service_uuid})")
            except Exception:
                missing_services.append(f"{service_class.__name__} (failed to instantiate)")

        # Check characteristics
        for char_class in char_classes:
            try:
                # Use class-level UUID resolution
                char_uuid: BluetoothUUID | None = char_class._resolve_class_uuid()  # type: ignore[attr-defined]
                if char_uuid is None:
                    missing_characteristics.append(f"{char_class.__name__} (failed to resolve UUID)")
                    continue
                # char_uuid is now narrowed to BluetoothUUID (non-None)
                char_info = uuid_registry.get_characteristic_info(char_uuid)
                if char_info is None:
                    missing_characteristics.append(f"{char_class.__name__} (UUID: {char_uuid})")
            except Exception:
                missing_characteristics.append(f"{char_class.__name__} (failed to instantiate)")

        # Report any missing entries
        error_messages = []
        if missing_services:
            error_messages.append(f"Services missing from YAML registry: {missing_services}")
        if missing_characteristics:
            error_messages.append(f"Characteristics missing from YAML registry: {missing_characteristics}")

        if error_messages:
            pytest.fail("YAML registry incomplete:\n" + "\n".join(error_messages))


class TestNameResolutionFallback:
    """Test name resolution fallback behavior when explicit names are not
    set.
    """

    def test_service_class_name_fallback(self) -> None:
        """Test that services without _service_name use class name
        resolution.
        """
        # Test with BatteryService which doesn't have _service_name set
        from bluetooth_sig.gatt.services.battery_service import BatteryService

        service = BatteryService()

        # Should have _service_name but it should be empty (using class name fallback)
        assert hasattr(service, "_service_name"), "BatteryService should have _service_name attribute"
        assert not service._service_name, "BatteryService _service_name should be empty"  # type: ignore[protected-access]

        # Should resolve UUID through class name
        uuid = service.uuid
        assert uuid == "180F", f"BatteryService should resolve to UUID 180F, got {uuid}"

        # Should get name from registry
        name = service.name
        assert name == "Battery", f"Expected 'Battery', got '{name}'"

    def test_characteristic_class_name_fallback(self) -> None:
        """Test that characteristics without _characteristic_name use class
        name resolution.
        """
        # Create a test characteristic class without explicit name
        from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic

        class TemperatureCharacteristic(CustomBaseCharacteristic):
            """Test characteristic without explicit name."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("AA112A6E-0000-1000-8000-00805F9B34FB"),
                name="Temperature",
                unit="°C",
                value_type=ValueType.FLOAT,
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
                return 0.0

            def encode_value(self, data: bytearray) -> bytearray:
                """Test implementation."""
                return bytearray([0, 0])

        # Test class-level resolution - the class name still resolves even though it's custom
        resolved_uuid = TemperatureCharacteristic._resolve_from_basic_registry_class()  # type: ignore[attr-defined]
        assert resolved_uuid is not None, "TemperatureCharacteristic class name should resolve from basic registry"
        assert resolved_uuid.short_form == "2A6E", (
            f"TemperatureCharacteristic should resolve to UUID 2A6E, got {resolved_uuid.short_form}"
        )

        # Now test instance
        char = TemperatureCharacteristic()

        # Should have _characteristic_name attribute (all characteristics have this)
        # but it should be None (not explicitly set in class definition)
        assert hasattr(char, "_characteristic_name"), "All characteristics should have _characteristic_name attribute"
        assert char._characteristic_name is None, (
            "Test characteristic should not have explicit _characteristic_name value"
        )  # type: ignore[protected-access]

        # Should get name from _info
        name = char.name
        assert name == "Temperature", f"Expected 'Temperature', got '{name}'"

    def test_service_explicit_name_override(self) -> None:
        """Test that services with _service_name override class name
        resolution.
        """
        from bluetooth_sig.gatt.services.generic_access import GenericAccessService

        service = GenericAccessService()

        # Should have explicit service name
        assert hasattr(service, "_service_name"), "GenericAccessService should have _service_name set"
        assert service._service_name == "GAP", (  # type: ignore[protected-access]
            f"Expected 'GAP', got '{service._service_name}'"  # type: ignore[protected-access]
        )

        # Should resolve UUID through explicit name, not class name
        uuid = service.uuid
        assert uuid == "1800", f"GenericAccessService should resolve to UUID 1800, got {uuid}"

        # Should get name from registry
        name = service.name
        assert name == "GAP", f"Expected 'GAP', got '{name}'"

    def test_characteristic_explicit_name_override(self) -> None:
        """Test that characteristics with _characteristic_name override class
        name resolution.
        """
        from bluetooth_sig.gatt.characteristics.uv_index import UVIndexCharacteristic

        char = UVIndexCharacteristic()

        # Should have explicit characteristic name
        assert hasattr(char, "_characteristic_name"), "UVIndexCharacteristic should have _characteristic_name set"
        assert char._characteristic_name == "UV Index", (  # type: ignore[protected-access]
            f"Expected 'UV Index', got '{char._characteristic_name}'"  # type: ignore[protected-access]
        )

        # Should resolve UUID through explicit name, not class name parsing
        uuid = char.uuid
        assert uuid == "2A76", f"UVIndexCharacteristic should resolve to UUID 2A76, got {uuid}"

        # Should get name from explicit name
        name = char.name
        assert name == "UV Index", f"Expected 'UV Index', got '{name}'"

    def test_class_name_parsing_edge_cases(self) -> None:
        """Test edge cases in class name parsing."""
        from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic

        # Test characteristic with complex class name
        class ModelNumberStringCharacteristic(CustomBaseCharacteristic):
            """Test complex characteristic name parsing."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("AA112A24-0000-1000-8000-00805F9B34FB"),
                name="Model Number String",
                unit="",
                value_type=ValueType.STRING,
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> str:
                return ""

            def encode_value(self, data: bytearray) -> bytearray:
                """Test implementation."""
                return bytearray()

        # Test class-level resolution - the class name still resolves even though it's custom
        resolved_uuid = ModelNumberStringCharacteristic._resolve_from_basic_registry_class()  # type: ignore[attr-defined]
        assert resolved_uuid is not None, (
            "ModelNumberStringCharacteristic class name should resolve from basic registry"
        )
        assert resolved_uuid == "2A24", (
            f"ModelNumberStringCharacteristic should resolve to UUID 2A24, got {resolved_uuid}"
        )

        # Now test instance
        char = ModelNumberStringCharacteristic()

        name = char.name
        assert name == "Model Number String", f"Expected 'Model Number String', got '{name}'"

    def test_fallback_failure_handling(self) -> None:
        """Test behavior when neither explicit name nor class name resolution
        works.
        """
        from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic

        class UnknownTestCharacteristic(CustomBaseCharacteristic):
            """Test characteristic that shouldn't exist in registry."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("1234"),
                name="Test Unknown Characteristic",
                unit="",
                value_type=ValueType.STRING,
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> str:
                return ""

            def encode_value(self, data: bytearray) -> bytearray:
                """Test implementation."""
                return bytearray()

        # Test class-level resolution should return None for unknown characteristic
        resolved_uuid = UnknownTestCharacteristic._resolve_from_basic_registry_class()  # type: ignore[attr-defined]
        assert resolved_uuid is None, "UnknownTestCharacteristic should not resolve UUID at class level"

        # Should allow creating instance with explicit info even if not in registry
        char = UnknownTestCharacteristic()
        assert char.uuid == BluetoothUUID("1234"), "Should use provided UUID"

    def test_current_services_name_resolution_strategy(self) -> None:
        """Test that current services use the expected name resolution
        strategy.
        """
        from bluetooth_sig.gatt.services.battery_service import BatteryService
        from bluetooth_sig.gatt.services.device_information import (
            DeviceInformationService,
        )
        from bluetooth_sig.gatt.services.environmental_sensing import (
            EnvironmentalSensingService,
        )
        from bluetooth_sig.gatt.services.generic_access import GenericAccessService

        # Services without explicit names (should use class name resolution)
        services_without_explicit_names = [
            (BatteryService, "180F", "Battery"),
            (EnvironmentalSensingService, "181A", "Environmental Sensing"),
            (DeviceInformationService, "180A", "Device Information"),
        ]

        for (
            service_class,
            expected_uuid,
            expected_name,
        ) in services_without_explicit_names:
            service = service_class()
            assert hasattr(service, "_service_name"), f"{service_class.__name__} should have _service_name attribute"
            assert not service._service_name, (  # type: ignore[protected-access]
                f"{service_class.__name__} _service_name should be empty"
            )
            assert service.uuid == expected_uuid
            assert service.name == expected_name

        # Services with explicit names (should use explicit name resolution)
        services_with_explicit_names = [
            (GenericAccessService, "1800", "GAP", "GAP"),
        ]

        for (
            service_class,
            expected_uuid,
            explicit_name,
            expected_name,
        ) in services_with_explicit_names:
            service = service_class()
            assert hasattr(service, "_service_name"), f"{service_class.__name__} should have _service_name"
            assert service._service_name == explicit_name  # type: ignore[protected-access]
            assert service.uuid == expected_uuid
            assert service.name == expected_name

    def test_current_characteristics_name_resolution_strategy(self) -> None:
        """Test that current characteristics use the expected name resolution
        strategy.
        """
        from bluetooth_sig.gatt.characteristics.battery_level import (
            BatteryLevelCharacteristic,
        )
        from bluetooth_sig.gatt.characteristics.uv_index import UVIndexCharacteristic

        # Characteristics with explicit names (should use explicit name resolution)
        chars_with_explicit_names = [
            (UVIndexCharacteristic, "2A76", "UV Index", "UV Index"),
        ]

        for (
            char_class,
            expected_uuid,
            explicit_name,
            expected_name,
        ) in chars_with_explicit_names:
            char = char_class()
            assert hasattr(char, "_characteristic_name"), f"{char_class.__name__} should have _characteristic_name"
            assert char._characteristic_name == explicit_name  # type: ignore[protected-access]
            assert char.uuid == expected_uuid
            assert char.name == expected_name

        # Characteristics without explicit names (should resolve from YAML)
        chars_without_explicit_names = [
            (BatteryLevelCharacteristic, "2A19", "Battery Level"),
        ]

        for (
            char_class,
            expected_uuid,
            expected_name,
        ) in chars_without_explicit_names:
            char_instance: BaseCharacteristic = char_class()  # Explicit type to fix mypy inference
            # Should NOT have explicit _characteristic_name attribute
            assert not hasattr(char_instance, "_characteristic_name") or char_instance._characteristic_name is None  # type: ignore[protected-access]
            assert char_instance.uuid == expected_uuid
            assert char_instance.name == expected_name


if __name__ == "__main__":
    # Run this file directly for debugging
    import sys

    sys.path.insert(0, "src")

    print("=== Discovering Services ===")
    discovered_services = discover_service_classes()
    for svc in discovered_services:
        print(f"  {svc.__name__}")

    print("\n=== Discovering Characteristics ===")
    discovered_characteristics = discover_characteristic_classes()
    for charac in discovered_characteristics:
        print(f"  {charac.__name__}")

    print(f"\nTotal Services: {len(discovered_services)}")
    print(f"Total Characteristics: {len(discovered_characteristics)}")
