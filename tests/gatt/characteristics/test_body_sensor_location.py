"""Tests for Body Sensor Location characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BodySensorLocation, BodySensorLocationCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBodySensorLocationCharacteristic(CommonCharacteristicTests):
    """Test suite for Body Sensor Location characteristic (0x2A38)."""

    characteristic_cls = BodySensorLocationCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
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

    def test_invalid_length(self, characteristic: BaseCharacteristic) -> None:
        """Test that invalid data length raises ValueError."""
        with pytest.raises(ValueError, match="requires exactly 1 byte"):
            characteristic.decode_value(bytearray([]))

        with pytest.raises(ValueError, match="requires exactly 1 byte"):
            characteristic.decode_value(bytearray([0x00, 0x00]))

    def test_invalid_value(self, characteristic: BaseCharacteristic) -> None:
        """Test that invalid location value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Body Sensor Location value"):
            characteristic.decode_value(bytearray([0x07]))  # Out of range

        with pytest.raises(ValueError, match="Invalid Body Sensor Location value"):
            characteristic.decode_value(bytearray([0xFF]))

    def test_encode_value(self, characteristic: BaseCharacteristic) -> None:
        """Test encoding body sensor location to bytes."""
        assert characteristic.encode_value(BodySensorLocation.WRIST) == bytearray([0x02])
        assert characteristic.encode_value(BodySensorLocation.CHEST) == bytearray([0x01])
        assert characteristic.encode_value(BodySensorLocation.FOOT) == bytearray([0x06])
