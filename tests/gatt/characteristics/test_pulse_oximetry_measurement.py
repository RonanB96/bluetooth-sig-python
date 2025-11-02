from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PLXFeatureFlags, PulseOximetryMeasurementCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement import (
    PulseOximetryData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPulseOximetryMeasurementCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return PulseOximetryMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2A5F is PLX Continuous Measurement
        return "2A5F"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        from datetime import datetime

        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x80, 0x00, 0x80]),  # flags=0, SpO2=0, pulse_rate=0
                expected_value=PulseOximetryData(spo2=0.0, pulse_rate=0.0),
                description="Minimal pulse oximetry data (SpO2=0%, pulse=0 bpm)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x62, 0x80, 0x48, 0x80]),  # flags=0, SpO2=98%, pulse_rate=72 bpm
                expected_value=PulseOximetryData(spo2=98.0, pulse_rate=72.0),
                description="Normal pulse oximetry data (SpO2=98%, pulse=72 bpm)",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x01, 0x62, 0x80, 0x48, 0x80, 0xD0, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00]
                ),  # flags=1, SpO2=98%, pulse_rate=72 bpm, timestamp=2000-01-01 00:00:00
                expected_value=PulseOximetryData(spo2=98.0, pulse_rate=72.0, timestamp=datetime(2000, 1, 1, 0, 0, 0)),
                description="Pulse oximetry with timestamp",
            ),
        ]

    def test_pulse_oximetry_without_context_backward_compatibility(self, characteristic: BaseCharacteristic) -> None:
        """Test that parsing works without context (backward compatibility)."""
        plx_data = bytearray([0x00, 0x62, 0x80, 0x48, 0x80])  # SpO2=98%, pulse=72 bpm
        result = characteristic.decode_value(plx_data, ctx=None)

        assert isinstance(result, PulseOximetryData)
        assert result.spo2 == 98.0
        assert result.pulse_rate == 72.0
        assert result.supported_features is None  # No context available

    def test_pulse_oximetry_with_plx_features_context(self, characteristic: BaseCharacteristic) -> None:
        """Test pulse oximetry parsing with PLX features from context."""
        from typing import cast

        from bluetooth_sig.gatt.context import CharacteristicContext
        from bluetooth_sig.types import CharacteristicData, CharacteristicDataProtocol, CharacteristicInfo
        from bluetooth_sig.types.uuid import BluetoothUUID

        # Mock context with PLX Features (0x2A60)
        # Example features: 0x0003 = Measurement Status Support + Device Status Support
        plx_features = CharacteristicData(
            info=CharacteristicInfo(
                uuid=BluetoothUUID("2A60"),
                name="PLX Features",
            ),
            value=PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT | PLXFeatureFlags.DEVICE_AND_SENSOR_STATUS_SUPPORT,
            raw_data=bytes([0x03, 0x00]),
            parse_success=True,
            error_message="",
            descriptors={},
        )

        # Use full UUID format to match translator behavior
        plx_features_uuid = BluetoothUUID("2A60").dashed_form
        ctx = CharacteristicContext(
            other_characteristics={
                plx_features_uuid: cast(CharacteristicDataProtocol, plx_features)
            }
        )

        # Parse with context
        plx_data = bytearray([0x00, 0x62, 0x80, 0x48, 0x80])  # SpO2=98%, pulse=72 bpm
        result = characteristic.decode_value(plx_data, ctx)

        assert result.spo2 == 98.0
        assert result.pulse_rate == 72.0
        assert (
            result.supported_features
            == PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT | PLXFeatureFlags.DEVICE_AND_SENSOR_STATUS_SUPPORT
        )

    def test_pulse_oximetry_with_various_plx_features(self, characteristic: BaseCharacteristic) -> None:
        """Test pulse oximetry with various PLX feature flags."""
        from typing import cast

        from bluetooth_sig.gatt.context import CharacteristicContext
        from bluetooth_sig.types import CharacteristicData, CharacteristicDataProtocol, CharacteristicInfo
        from bluetooth_sig.types.uuid import BluetoothUUID

        # Test various feature combinations
        feature_values = [
            PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT,
            PLXFeatureFlags.DEVICE_AND_SENSOR_STATUS_SUPPORT,
            PLXFeatureFlags.MEASUREMENT_STORAGE_SUPPORT,
            PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT
            | PLXFeatureFlags.DEVICE_AND_SENSOR_STATUS_SUPPORT
            | PLXFeatureFlags.MEASUREMENT_STORAGE_SUPPORT,
            PLXFeatureFlags(0xFFFF),  # All features enabled
        ]

        for feature_value in feature_values:
            plx_features = CharacteristicData(
                info=CharacteristicInfo(
                    uuid=BluetoothUUID("2A60"),
                    name="PLX Features",
                ),
                value=feature_value,
                raw_data=int(feature_value).to_bytes(2, byteorder="little"),
                parse_success=True,
                error_message="",
                descriptors={},
            )

            # Use full UUID format to match translator behavior
            plx_features_uuid = BluetoothUUID("2A60").dashed_form
            ctx = CharacteristicContext(
                other_characteristics={
                    plx_features_uuid: cast(CharacteristicDataProtocol, plx_features)
                }
            )

            plx_data = bytearray([0x00, 0x5F, 0x80, 0x4C, 0x80])  # SpO2=95%, pulse=76 bpm
            result = characteristic.decode_value(plx_data, ctx)

            assert result.spo2 == 95.0
            assert result.pulse_rate == 76.0
            assert result.supported_features == feature_value

    def test_pulse_oximetry_context_with_missing_plx_features(self, characteristic: BaseCharacteristic) -> None:
        """Test that pulse oximetry works when context exists but PLX features don't."""
        from bluetooth_sig.gatt.context import CharacteristicContext

        # Context without PLX features
        ctx = CharacteristicContext(other_characteristics={})

        plx_data = bytearray([0x00, 0x62, 0x80, 0x48, 0x80])  # SpO2=98%, pulse=72 bpm
        result = characteristic.decode_value(plx_data, ctx)

        assert result.spo2 == 98.0
        assert result.pulse_rate == 72.0
        assert result.supported_features is None  # Graceful handling of missing context data
