"""Tests for PLX Features characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import PLXFeatureFlags, PLXFeaturesCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPLXFeaturesCharacteristic(CommonCharacteristicTests):
    """Test suite for PLX Features characteristic (0x2A60)."""

    characteristic_cls = PLXFeaturesCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return PLXFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A60"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=PLXFeatureFlags(0x0000),
                description="PLX Features: No features",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT,
                description="PLX Features: Measurement Status Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00]),
                expected_value=PLXFeatureFlags.DEVICE_AND_SENSOR_STATUS_SUPPORT,
                description="PLX Features: Device and Sensor Status Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x00]),
                expected_value=PLXFeatureFlags.MEASUREMENT_STORAGE_SUPPORT,
                description="PLX Features: Measurement Storage Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x00]),
                expected_value=PLXFeatureFlags.TIMESTAMP_SUPPORT,
                description="PLX Features: Timestamp Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x00]),
                expected_value=PLXFeatureFlags.SPO2PR_FAST_SUPPORT,
                description="PLX Features: SpO2PR-Fast Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x20, 0x00]),
                expected_value=PLXFeatureFlags.SPO2PR_SLOW_SUPPORT,
                description="PLX Features: SpO2PR-Slow Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00]),
                expected_value=PLXFeatureFlags.PULSE_AMPLITUDE_INDEX_SUPPORT,
                description="PLX Features: Pulse Amplitude Index Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x00]),
                expected_value=PLXFeatureFlags.MULTIPLE_BONDS_SUPPORT,
                description="PLX Features: Multiple Bonds Support",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x07, 0x00]),
                expected_value=PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT
                | PLXFeatureFlags.DEVICE_AND_SENSOR_STATUS_SUPPORT
                | PLXFeatureFlags.MEASUREMENT_STORAGE_SUPPORT,
                description="PLX Features: All basic features",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x00]),
                expected_value=PLXFeatureFlags(0x00FF),
                description="PLX Features: All defined features (lower byte)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x80]),
                expected_value=PLXFeatureFlags(0x8000),
                description="PLX Features: Reserved upper byte bit",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]),
                expected_value=PLXFeatureFlags(0xFFFF),
                description="PLX Features: All bits set (including reserved)",
            ),
        ]

    def test_invalid_length(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test that invalid data length results in parse failure."""
        # parse_value returns parse_success=False for insufficient data
        result = characteristic.parse_value(bytearray([]))
        assert result.parse_success is False

        result = characteristic.parse_value(bytearray([0x00]))
        assert result.parse_success is False

    def test_encode_value(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test encoding PLX features to bytes."""
        assert characteristic.build_value(PLXFeatureFlags(0x0000)) == bytearray([0x00, 0x00])
        assert characteristic.build_value(PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT) == bytearray([0x01, 0x00])
        assert characteristic.build_value(
            PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT
            | PLXFeatureFlags.DEVICE_AND_SENSOR_STATUS_SUPPORT
            | PLXFeatureFlags.MEASUREMENT_STORAGE_SUPPORT
        ) == bytearray([0x07, 0x00])
        assert characteristic.build_value(PLXFeatureFlags(0xFFFF)) == bytearray([0xFF, 0xFF])
