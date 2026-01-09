"""Test glucose multi-characteristic integration and service functionality."""

from __future__ import annotations

import logging

import pytest

from bluetooth_sig.core import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    GlucoseFeatureCharacteristic,
    GlucoseMeasurementCharacteristic,
    GlucoseMeasurementContextCharacteristic,
)
from bluetooth_sig.gatt.services.glucose import GlucoseService
from bluetooth_sig.types.gatt_enums import CharacteristicName
from bluetooth_sig.types.gatt_services import ServiceDiscoveryData
from bluetooth_sig.types.uuid import BluetoothUUID

from .test_service_common import CommonServiceTests


class TestGlucoseService(CommonServiceTests):
    """Test Glucose Service functionality."""

    @pytest.fixture
    def service(self) -> GlucoseService:
        """Fixture providing a glucose service."""
        return GlucoseService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for glucose service."""
        return "1808"

    @pytest.fixture
    def expected_name(self) -> str:
        """Expected name for glucose service."""
        return "Glucose"

    def test_glucose_service_characteristics(self, service: GlucoseService) -> None:
        """Test that glucose service has correct characteristics."""
        expected_chars = service.get_expected_characteristics()
        required_chars = service.get_required_characteristics()

        # Check expected characteristics
        assert CharacteristicName.GLUCOSE_MEASUREMENT in expected_chars
        assert CharacteristicName.GLUCOSE_MEASUREMENT_CONTEXT in expected_chars
        assert CharacteristicName.GLUCOSE_FEATURE in expected_chars
        assert len(expected_chars) == 3

        # Check required characteristics
        assert CharacteristicName.GLUCOSE_MEASUREMENT in required_chars
        assert CharacteristicName.GLUCOSE_FEATURE in required_chars
        assert len(required_chars) == 2

    def test_glucose_service_registration(self) -> None:
        """Test that glucose service is properly registered."""
        from bluetooth_sig.gatt.services import GattServiceRegistry

        # Check that glucose service is in the registry
        service_class = GattServiceRegistry.get_service_class("1808")
        assert service_class == GlucoseService

        # Check that glucose service can be instantiated correctly
        glucose_service = service_class()
        assert glucose_service.uuid == "1808"

    def test_glucose_characteristics_registration(self) -> None:
        """Test that glucose characteristics are properly registered."""
        from bluetooth_sig.gatt.characteristics import CharacteristicRegistry

        # Test Glucose Measurement
        gm_class = CharacteristicRegistry.get_characteristic_class_by_uuid("2A18")
        assert gm_class == GlucoseMeasurementCharacteristic

        # Test Glucose Measurement Context
        gmc_class = CharacteristicRegistry.get_characteristic_class_by_uuid("2A34")
        assert gmc_class == GlucoseMeasurementContextCharacteristic

        # Test Glucose Feature
        gf_class = CharacteristicRegistry.get_characteristic_class_by_uuid("2A51")
        assert gf_class == GlucoseFeatureCharacteristic

    def test_glucose_service_creation(self) -> None:
        """Test glucose service creation with characteristics."""
        from bluetooth_sig.gatt.services import GattServiceRegistry

        # Use characteristic classes to get proper SIG UUIDs
        glucose_measurement_char = GlucoseMeasurementCharacteristic()
        glucose_context_char = GlucoseMeasurementContextCharacteristic()
        glucose_feature_char = GlucoseFeatureCharacteristic()

        characteristics: ServiceDiscoveryData = {
            glucose_measurement_char.uuid: glucose_measurement_char.info,
            glucose_context_char.uuid: glucose_context_char.info,
            glucose_feature_char.uuid: glucose_feature_char.info,
        }

        service = GattServiceRegistry.create_service(BluetoothUUID("1808"), characteristics)
        assert service is not None
        assert isinstance(service, GlucoseService)
        assert len(service.characteristics) == 3

    def test_glucose_context_with_measurement_context(self) -> None:
        """Test parsing glucose measurement and context together with sequence number matching."""
        translator = BluetoothSIGTranslator()

        # Create matching glucose measurement and context with same sequence number (42)
        # Glucose Measurement: Flags + Seq(42) + Timestamp + Glucose
        glucose_data = bytearray(
            [
                0x00,  # flags: no optional fields, mg/dL unit
                0x2A,
                0x00,  # sequence: 42
                0xE8,
                0x07,
                0x03,
                0x0F,
                0x0E,
                0x1E,
                0x2D,  # timestamp: 2024-03-15 14:30:45
                0x80,
                0x17,  # glucose: 120.0 mg/dL (SFLOAT)
            ]
        )

        # Glucose Context: Flags + Seq(42)
        context_data = bytearray(
            [
                0x00,  # flags: no optional fields
                0x2A,
                0x00,  # sequence: 42 (matches measurement)
            ]
        )

        # Parse both characteristics together
        char_data: dict[str, bytes] = {
            "00002A18-0000-1000-8000-00805F9B34FB": bytes(glucose_data),  # Glucose Measurement
            "00002A34-0000-1000-8000-00805F9B34FB": bytes(context_data),  # Glucose Measurement Context
        }

        results = translator.parse_characteristics(char_data)

        # Both should parse successfully
        assert len(results) == 2

        # Check sequence numbers match
        glucose_result = results["00002A18-0000-1000-8000-00805F9B34FB"]
        context_result = results["00002A34-0000-1000-8000-00805F9B34FB"]

        assert glucose_result is not None
        assert context_result is not None
        assert glucose_result.sequence_number == 42
        assert context_result.sequence_number == 42

    def test_glucose_context_sequence_mismatch_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that mismatched sequence numbers generate a warning."""
        translator = BluetoothSIGTranslator()

        # Create glucose measurement and context with DIFFERENT sequence numbers
        glucose_data = bytearray(
            [
                0x00,  # flags
                0x2A,
                0x00,  # sequence: 42
                0xE8,
                0x07,
                0x03,
                0x0F,
                0x0E,
                0x1E,
                0x2D,  # timestamp
                0x80,
                0x17,  # glucose: 120.0 mg/dL
            ]
        )

        context_data = bytearray(
            [
                0x00,  # flags
                0x63,
                0x00,  # sequence: 99 (MISMATCH!)
            ]
        )

        char_data: dict[str, bytes] = {
            "00002A18-0000-1000-8000-00805F9B34FB": bytes(glucose_data),
            "00002A34-0000-1000-8000-00805F9B34FB": bytes(context_data),
        }

        # Parse both - should succeed but log warning
        with caplog.at_level(logging.WARNING):
            results = translator.parse_characteristics(char_data)

        # Both should still parse successfully (values returned directly)
        assert len(results) == 2

        # Check that warning was logged about mismatch
        assert any("does not match" in record.message for record in caplog.records)
