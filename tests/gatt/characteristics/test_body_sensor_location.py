"""Tests for Body Sensor Location characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import BodySensorLocation, BodySensorLocationCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBodySensorLocationCharacteristic(CommonCharacteristicTests):
    """Test suite for Body Sensor Location characteristic (0x2A38)."""

    characteristic_cls = BodySensorLocationCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return BodySensorLocationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A38"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=BodySensorLocation.OTHER,
                description="Body Sensor Location: Other",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=BodySensorLocation.CHEST,
                description="Body Sensor Location: Chest",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=BodySensorLocation.WRIST,
                description="Body Sensor Location: Wrist",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=BodySensorLocation.FINGER,
                description="Body Sensor Location: Finger",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]),
                expected_value=BodySensorLocation.HAND,
                description="Body Sensor Location: Hand",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=BodySensorLocation.EAR_LOBE,
                description="Body Sensor Location: Ear Lobe",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x06]),
                expected_value=BodySensorLocation.FOOT,
                description="Body Sensor Location: Foot",
            ),
        ]

    def test_invalid_length(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test that invalid data length raises error."""
        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        # Empty data - will fail when trying to access data[0]
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([]))
        assert "need 1 bytes" in str(exc_info.value).lower() or "insufficient" in str(exc_info.value).lower()

        # Too much data - characteristic only reads first byte, extra bytes ignored
        result = characteristic.parse_value(bytearray([0x00, 0x00]))
        # Should succeed, only first byte is read
        assert result == BodySensorLocation.OTHER

    def test_invalid_value(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test that invalid location value results in parse failure."""
        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        # parse_value now raises CharacteristicParseError for invalid values
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x07]))  # Out of range
        assert "BodySensorLocation" in str(exc_info.value)

        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0xFF]))
        assert "BodySensorLocation" in str(exc_info.value)

    def test_encode_value(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test encoding body sensor location to bytes."""
        assert characteristic.build_value(BodySensorLocation.WRIST) == bytearray([0x02])
        assert characteristic.build_value(BodySensorLocation.CHEST) == bytearray([0x01])
        assert characteristic.build_value(BodySensorLocation.FOOT) == bytearray([0x06])
