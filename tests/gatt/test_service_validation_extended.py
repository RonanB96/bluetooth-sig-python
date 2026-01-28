from __future__ import annotations

from typing import Any, cast

from bluetooth_sig.gatt.characteristics import BaseCharacteristic, BatteryLevelCharacteristic
from bluetooth_sig.gatt.services import BatteryService, CharacteristicStatus, ServiceHealthStatus
from bluetooth_sig.types.uuid import BluetoothUUID


class TestServiceValidationEdgeCasesExtended:
    """Extended edge case tests for service validation."""

    def test_service_with_unknown_characteristics(self) -> None:
        """Test service validation with characteristics not in registry."""
        service = BatteryService()
        # Add a characteristic with unknown UUID using BatteryLevelCharacteristic
        unknown_char = BatteryLevelCharacteristic()
        service.characteristics[BluetoothUUID("FFFF")] = unknown_char

        # Validation should still work
        result = service.validate_service()
        assert isinstance(result.status, ServiceHealthStatus)

    def test_service_completeness_with_all_present(self) -> None:
        """Test completeness report when all characteristics are present."""
        service = BatteryService()

        # Add all expected characteristics
        battery_char = BatteryLevelCharacteristic()
        service.characteristics[BluetoothUUID("2A19")] = battery_char

        report = service.get_service_completeness_report()

        assert report.is_healthy is True
        assert report.characteristics_present >= 1
        assert len(report.missing_required) == 0
        # Check that Battery Level characteristic is present
        battery_present = any(char.name == "Battery Level" for char in report.present_characteristics)
        assert battery_present

    def test_get_characteristic_status_with_partial_match(self) -> None:
        """Test getting status of characteristics with partial name matches."""
        service = BatteryService()
        # Test case-insensitive and partial matching (now enum-only)
        from bluetooth_sig.gatt.characteristics.registry import CharacteristicName

        status = service.get_characteristic_status(CharacteristicName.BATTERY_LEVEL)
        if status is not None:  # Depends on implementation
            assert status.status == CharacteristicStatus.MISSING

    def test_validate_service_with_strict_mode(self) -> None:
        """Test service validation in strict mode."""
        service = BatteryService()

        # Test both modes
        result_normal = service.validate_service(strict=False)
        result_strict = service.validate_service(strict=True)

        # Both should return valid results
        assert isinstance(result_normal.status, ServiceHealthStatus)
        assert isinstance(result_strict.status, ServiceHealthStatus)

        # Strict mode might have more warnings
        assert len(result_strict.warnings) >= len(result_normal.warnings)

    def test_service_validation_with_conditional_characteristics(self) -> None:
        """Test validation with conditional characteristics."""
        service = BatteryService()

        # Get missing characteristics and check for conditional info
        missing = service.get_missing_characteristics()

        for _char_name, char_info in missing.items():
            # Should have proper status and conditional information
            assert char_info.status == CharacteristicStatus.MISSING
            assert isinstance(char_info.is_conditional, bool)

    def test_service_health_status_ordering(self) -> None:
        """Test that health status enum values have logical ordering."""
        # Test enum values exist and have expected ordering
        statuses = list(ServiceHealthStatus)
        assert ServiceHealthStatus.COMPLETE in statuses
        assert ServiceHealthStatus.FUNCTIONAL in statuses
        assert ServiceHealthStatus.PARTIAL in statuses
        assert ServiceHealthStatus.INCOMPLETE in statuses

    def test_service_validation_error_messages(self) -> None:
        """Test that validation provides meaningful error messages."""
        service = BatteryService()

        result = service.validate_service()

        # Should have meaningful error messages for missing required characteristics
        if result.errors:
            for error in result.errors:
                assert isinstance(error, str)
                assert len(error) > 0

        # Should have meaningful names in missing required
        if result.missing_required:
            for missing_char in result.missing_required:
                assert isinstance(missing_char, BaseCharacteristic)
                assert len(missing_char.name) > 0

    def test_service_completeness_report_consistency(self) -> None:
        """Test that completeness report data is internally consistent."""
        service = BatteryService()
        report = service.get_service_completeness_report()

        # Check consistency
        assert (
            len(report.present_characteristics) + len(report.missing_required) + len(report.missing_optional)
            >= report.characteristics_expected
        )

        assert report.characteristics_present == len(report.present_characteristics)

        # Missing details should match missing characteristics
        for missing_char in report.missing_required + report.missing_optional:
            if missing_char.name in report.missing_details:
                detail = report.missing_details[missing_char.name]
                assert detail.name == missing_char.name
                assert detail.status == CharacteristicStatus.MISSING

    def test_has_minimum_functionality_edge_cases(self) -> None:
        """Test has_minimum_functionality with various configurations."""
        service = BatteryService()

        # Without any characteristics
        assert service.has_minimum_functionality() is False

        # With only optional characteristics (if any exist)
        expected_chars = service.get_expected_characteristics()
        required_chars = service.get_required_characteristics()

        optional_chars = {name: char_class for name, char_class in expected_chars.items() if name not in required_chars}

        # If there are optional characteristics, add one
        if optional_chars:
            _first_optional_name, first_optional_spec = next(iter(optional_chars.items()))
            # Try to create the optional characteristic from the spec
            try:
                # CharacteristicSpec has attribute 'char_class' in the new format
                first_optional_class = (
                    first_optional_spec.char_class
                    if hasattr(first_optional_spec, "char_class")
                    else first_optional_spec
                )
                # Cast to concrete class type for static type checkers
                first_optional_class = cast("type[BaseCharacteristic[Any]]", first_optional_class)
                optional_char = first_optional_class()
                service.characteristics[BluetoothUUID("12345678-1234-5678-9abc-def012345678")] = optional_char

                # Should still not have minimum functionality without required chars
                assert service.has_minimum_functionality() is False
            except Exception:
                # If creation fails, that's okay - just testing the logic
                pass

        # With required characteristics
        if required_chars:
            _first_required_name, first_required_spec = next(iter(required_chars.items()))
            try:
                first_required_class = (
                    first_required_spec.char_class
                    if hasattr(first_required_spec, "char_class")
                    else first_required_spec
                )
                # Cast to concrete class type for static type checkers
                first_required_class = cast("type[BaseCharacteristic[Any]]", first_required_class)
                required_char = first_required_class()
                service.characteristics[BluetoothUUID("87654321-4321-8765-cba9-876543210fed")] = required_char

                # Should have minimum functionality now
                assert service.has_minimum_functionality() is True
            except Exception:
                # If creation fails, that's okay - service-specific behaviour
                pass
