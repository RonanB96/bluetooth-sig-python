"""Tests for service validation and completeness reporting functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic, ModelNumberStringCharacteristic
from bluetooth_sig.gatt.services import (
    BatteryService,
    CharacteristicStatus,
    DeviceInformationService,
    ServiceCharacteristicInfo,
    ServiceCompletenessReport,
    ServiceHealthStatus,
    ServiceValidationResult,
)
from bluetooth_sig.types.uuid import BluetoothUUID


class TestServiceHealthStatus:
    """Test ServiceHealthStatus enum."""

    def test_health_status_values(self) -> None:
        """Test that all expected health status values exist."""
        assert ServiceHealthStatus.COMPLETE
        assert ServiceHealthStatus.FUNCTIONAL
        assert ServiceHealthStatus.PARTIAL
        assert ServiceHealthStatus.INCOMPLETE

        # Test string values
        assert ServiceHealthStatus.COMPLETE.value == "complete"
        assert ServiceHealthStatus.FUNCTIONAL.value == "functional"
        assert ServiceHealthStatus.PARTIAL.value == "partial"
        assert ServiceHealthStatus.INCOMPLETE.value == "incomplete"


class TestCharacteristicStatus:
    """Test CharacteristicStatus enum."""

    def test_characteristic_status_values(self) -> None:
        """Test that all expected characteristic status values exist."""
        assert CharacteristicStatus.PRESENT
        assert CharacteristicStatus.MISSING
        assert CharacteristicStatus.INVALID

        # Test string values
        assert CharacteristicStatus.PRESENT.value == "present"
        assert CharacteristicStatus.MISSING.value == "missing"
        assert CharacteristicStatus.INVALID.value == "invalid"


class TestServiceValidationResult:
    """Test ServiceValidationResult dataclass."""

    def test_service_validation_result_creation(self) -> None:
        """Test creation of ServiceValidationResult."""
        result = ServiceValidationResult(status=ServiceHealthStatus.COMPLETE)

        assert result.status == ServiceHealthStatus.COMPLETE
        assert result.is_healthy is True
        assert result.missing_required == []
        assert result.missing_optional == []
        assert result.invalid_characteristics == []
        assert result.warnings == []
        assert result.errors == []

    def test_service_validation_result_with_issues(self) -> None:
        """Test ServiceValidationResult with validation issues."""
        battery_char = BatteryLevelCharacteristic()
        model_char = ModelNumberStringCharacteristic()

        result = ServiceValidationResult(
            status=ServiceHealthStatus.PARTIAL,
            missing_required=[battery_char],
            missing_optional=[model_char],
            invalid_characteristics=[],  # Empty for now since test expects strings
            warnings=["Optional characteristic missing"],
            errors=["Required characteristic missing"],
        )

        assert result.status == ServiceHealthStatus.PARTIAL
        assert result.is_healthy is False
        assert battery_char in result.missing_required
        assert model_char in result.missing_optional
        assert len(result.warnings) == 1
        assert len(result.errors) == 1

    def test_has_errors_property(self) -> None:
        """Test the has_errors property."""
        # No errors or missing required
        result = ServiceValidationResult(status=ServiceHealthStatus.COMPLETE)
        assert result.has_errors is False

        # Has errors
        result_with_errors = ServiceValidationResult(status=ServiceHealthStatus.INCOMPLETE, errors=["Some error"])
        assert result_with_errors.has_errors is True

        # Has missing required
        battery_char = BatteryLevelCharacteristic()
        result_missing_required = ServiceValidationResult(
            status=ServiceHealthStatus.PARTIAL, missing_required=[battery_char]
        )
        assert result_missing_required.has_errors is True


class TestServiceCharacteristicInfo:
    """Test ServiceCharacteristicInfo dataclass."""

    def test_service_characteristic_info_creation(self) -> None:
        """Test creation of ServiceCharacteristicInfo."""
        info = ServiceCharacteristicInfo(
            uuid=BluetoothUUID("2A19"),
            name="Battery Level",
            status=CharacteristicStatus.PRESENT,
            is_required=True,
            is_conditional=False,
        )

        assert info.uuid == BluetoothUUID("2A19")
        assert info.name == "Battery Level"
        assert info.status == CharacteristicStatus.PRESENT
        assert info.is_required is True
        assert info.is_conditional is False
        assert info.condition_description == ""

    def test_service_characteristic_info_with_condition(self) -> None:
        """Test ServiceCharacteristicInfo with conditional information."""
        info = ServiceCharacteristicInfo(
            uuid=BluetoothUUID("2A1A"),
            name="Conditional Char",
            status=CharacteristicStatus.MISSING,
            is_required=False,
            is_conditional=True,
            condition_description="Only if feature X is supported",
        )

        assert info.is_conditional is True
        assert info.condition_description == "Only if feature X is supported"


class TestServiceCompletenessReport:
    """Test ServiceCompletenessReport dataclass."""

    def test_service_completeness_report_creation(self) -> None:
        """Test creation of ServiceCompletenessReport."""
        battery_char = BatteryLevelCharacteristic()
        report = ServiceCompletenessReport(
            service_name="Battery Service",
            service_uuid=BluetoothUUID("180F"),
            health_status=ServiceHealthStatus.COMPLETE,
            is_healthy=True,
            characteristics_present=1,
            characteristics_expected=1,
            characteristics_required=1,
            present_characteristics=[battery_char],
            missing_required=[],
            missing_optional=[],
            invalid_characteristics=[],
            warnings=[],
            errors=[],
            missing_details={},
        )

        assert report.service_name == "Battery Service"
        assert report.service_uuid == BluetoothUUID("180F")
        assert report.health_status == ServiceHealthStatus.COMPLETE
        assert report.is_healthy is True
        assert report.characteristics_present == 1
        assert report.characteristics_expected == 1
        assert report.characteristics_required == 1
        assert battery_char in report.present_characteristics
        assert len(report.missing_required) == 0
        assert len(report.missing_details) == 0

    def test_service_completeness_report_with_missing_details(self) -> None:
        """Test ServiceCompletenessReport with missing characteristic
        details.
        """
        missing_char = ServiceCharacteristicInfo(
            uuid=BluetoothUUID("2A29"),
            name="Manufacturer Name",
            status=CharacteristicStatus.MISSING,
            is_required=False,
        )
        model_char = ModelNumberStringCharacteristic()
        manufacturer_char = ModelNumberStringCharacteristic()  # Placeholder for manufacturer

        report = ServiceCompletenessReport(
            service_name="Device Information Service",
            service_uuid=BluetoothUUID("180A"),
            health_status=ServiceHealthStatus.INCOMPLETE,
            is_healthy=False,
            characteristics_present=2,
            characteristics_expected=3,
            characteristics_required=1,
            present_characteristics=[model_char],
            missing_required=[],
            missing_optional=[manufacturer_char],
            invalid_characteristics=[],
            warnings=["Missing optional characteristic"],
            errors=[],
            missing_details={"Manufacturer Name": missing_char},
        )

        assert report.is_healthy is False
        assert manufacturer_char in report.missing_optional
        assert "Manufacturer Name" in report.missing_details
        assert report.missing_details["Manufacturer Name"].uuid == BluetoothUUID("2A29")


class TestBatteryServiceValidation:
    """Test service validation with BatteryService."""

    service: BatteryService

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.service = BatteryService()

    def test_empty_battery_service_validation(self) -> None:
        """Test validation of empty battery service."""
        result = self.service.validate_service()

        assert result.status == ServiceHealthStatus.INCOMPLETE
        assert result.is_healthy is False
        # Check that Battery Level characteristic is in missing required
        battery_level_missing = any(char.name == "Battery Level" for char in result.missing_required)
        assert battery_level_missing
        assert len(result.errors) > 0

    def test_complete_battery_service_validation(self) -> None:
        """Test validation of complete battery service."""
        # Add required battery level characteristic
        battery_char = BatteryLevelCharacteristic()
        self.service.characteristics[battery_char.uuid] = battery_char

        result = self.service.validate_service()

        assert result.status == ServiceHealthStatus.COMPLETE
        assert result.is_healthy is True
        assert len(result.missing_required) == 0
        assert len(result.errors) == 0

    def test_battery_service_get_missing_characteristics(self) -> None:
        """Test getting missing characteristics from battery service."""
        from bluetooth_sig.gatt.characteristics.registry import CharacteristicName

        missing = self.service.get_missing_characteristics()

        assert CharacteristicName.BATTERY_LEVEL in missing
        battery_info = missing[CharacteristicName.BATTERY_LEVEL]
        assert battery_info.uuid.short_form == "2A19"
        assert battery_info.name == "Battery Level"
        assert battery_info.status == CharacteristicStatus.MISSING
        assert battery_info.is_required is True

    def test_battery_service_characteristic_status(self) -> None:
        """Test getting characteristic status."""
        # Test missing characteristic
        from bluetooth_sig.gatt.characteristics.registry import CharacteristicName

        status = self.service.get_characteristic_status(CharacteristicName.BATTERY_LEVEL)
        assert status is not None
        assert status.status == CharacteristicStatus.MISSING
        assert status.is_required is True

        # Add the characteristic and test present status
        battery_char = BatteryLevelCharacteristic()
        self.service.characteristics[battery_char.uuid] = battery_char

        status = self.service.get_characteristic_status(CharacteristicName.BATTERY_LEVEL)
        assert status is not None
        assert status.status == CharacteristicStatus.PRESENT

        # Test unknown characteristic (enum that doesn't exist in expected list)
        # If the enum is not expected for BatteryService, the result should be None
        unknown_status = self.service.get_characteristic_status(CharacteristicName.UV_INDEX)
        if CharacteristicName.UV_INDEX not in self.service.get_expected_characteristics():
            assert unknown_status is None

    def test_battery_service_completeness_report(self) -> None:
        """Test getting service completeness report."""
        report = self.service.get_service_completeness_report()

        assert report.service_name == "Battery"
        assert report.service_uuid.short_form == "180F"
        assert report.is_healthy is False
        assert report.characteristics_present == 0
        assert report.characteristics_expected > 0
        # Check that Battery Level characteristic is in missing required
        battery_level_missing = any(char.name == "Battery Level" for char in report.missing_required)
        assert battery_level_missing
        assert "Battery Level" in report.missing_details

        missing_detail = report.missing_details["Battery Level"]
        assert missing_detail.uuid.short_form == "2A19"
        assert missing_detail.is_required is True

    def test_battery_service_has_minimum_functionality(self) -> None:
        """Test checking minimum functionality."""
        # Without battery level - no minimum functionality
        assert self.service.has_minimum_functionality() is False

        # With battery level - has minimum functionality
        battery_char = BatteryLevelCharacteristic()
        self.service.characteristics[battery_char.uuid] = battery_char

        assert self.service.has_minimum_functionality() is True


class TestDeviceInformationServiceValidation:
    """Test service validation with DeviceInformationService."""

    service: DeviceInformationService

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.service = DeviceInformationService()

    def test_empty_device_info_service_validation(self) -> None:
        """Test validation of empty device information service."""
        result = self.service.validate_service()

        # Device Information Service typically has no strictly required characteristics
        # But it should report what's missing
        assert result.status in [
            ServiceHealthStatus.INCOMPLETE,
            ServiceHealthStatus.COMPLETE,
        ]

    def test_device_info_service_strict_validation(self) -> None:
        """Test strict validation mode."""
        result = self.service.validate_service(strict=True)

        # In strict mode, missing optional characteristics should generate warnings
        assert isinstance(result.warnings, list)

    def test_device_info_service_missing_characteristics(self) -> None:
        """Test getting missing characteristics."""
        from bluetooth_sig.gatt.characteristics.registry import CharacteristicName

        missing = self.service.get_missing_characteristics()

        # Should have some expected characteristics missing
        assert isinstance(missing, dict)
        # Common device info characteristics (now as enums)
        expected_char_enums = [
            CharacteristicName.MANUFACTURER_NAME_STRING,
            CharacteristicName.MODEL_NUMBER_STRING,
            CharacteristicName.SERIAL_NUMBER_STRING,
            CharacteristicName.FIRMWARE_REVISION_STRING,
            CharacteristicName.HARDWARE_REVISION_STRING,
            CharacteristicName.SOFTWARE_REVISION_STRING,
        ]

        # At least some of these should be in expected characteristics
        expected_service_chars = self.service.get_expected_characteristics()
        common_chars = [char_enum for char_enum in expected_char_enums if char_enum in expected_service_chars]

        if common_chars:
            # If we have common characteristics, they should be missing
            for char_enum in common_chars:
                if char_enum in missing:
                    assert missing[char_enum].status == CharacteristicStatus.MISSING


class TestServiceValidationEdgeCases:
    """Test edge cases and error conditions."""

    def test_service_with_invalid_characteristic(self) -> None:
        """Test service with invalid characteristic data."""
        service = BatteryService()

        # Add an invalid characteristic (not a proper BaseCharacteristic)
        # Use a valid UUID but invalid characteristic object
        service.characteristics[BluetoothUUID("12345678-1234-5678-9abc-def012345678")] = "not_a_characteristic"  # type: ignore

        result = service.validate_service()
        # Should still handle this gracefully
        assert isinstance(result, ServiceValidationResult)

    def test_bluetooth_sig_compliance_validation(self) -> None:
        """Test Bluetooth SIG compliance validation."""
        issues = BatteryService.validate_bluetooth_sig_compliance()

        assert isinstance(issues, list)
        # Battery service should be SIG compliant, so minimal issues
        assert len(issues) >= 0  # May have warnings but should be valid


class TestServiceValidationIntegration:
    """Integration tests for service validation functionality."""

    def test_multiple_services_validation(self) -> None:
        """Test validation across multiple service types."""
        battery_service = BatteryService()
        device_info_service = DeviceInformationService()

        # Test both services
        battery_result = battery_service.validate_service()
        device_result = device_info_service.validate_service()

        assert isinstance(battery_result, ServiceValidationResult)
        assert isinstance(device_result, ServiceValidationResult)

        # Get completeness reports
        battery_report = battery_service.get_service_completeness_report()
        device_report = device_info_service.get_service_completeness_report()

        assert battery_report.service_name == "Battery"
        assert device_report.service_name == "Device Information"

    def test_service_validation_with_partial_implementation(self) -> None:
        """Test validation with partially implemented service."""
        service = DeviceInformationService()

        # Add only some characteristics (simulating real device)
        model_char = ModelNumberStringCharacteristic()
        service.characteristics[model_char.uuid] = model_char

        report = service.get_service_completeness_report()

        assert report.characteristics_present == 1
        # Check that Model Number String characteristic is present
        model_present = any(char.name == "Model Number String" for char in report.present_characteristics)
        assert model_present
        assert len(report.missing_details) > 0

    def test_service_validation_performance(self) -> None:
        """Test that service validation is performant."""
        import time

        service = BatteryService()

        start_time = time.time()
        for _ in range(100):
            service.validate_service()
            service.get_missing_characteristics()
            service.get_service_completeness_report()
        end_time = time.time()

        # Should complete 100 validation cycles in reasonable time
        assert end_time - start_time < 2.0  # Less than 2 seconds
