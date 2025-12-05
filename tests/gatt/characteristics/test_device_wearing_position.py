"""Tests for Device Wearing Position characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import DeviceWearingPositionCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDeviceWearingPositionCharacteristic(CommonCharacteristicTests):
    """Test suite for Device Wearing Position characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds device wearing position-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> DeviceWearingPositionCharacteristic:
        """Return a Device Wearing Position characteristic instance."""
        return DeviceWearingPositionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Device Wearing Position characteristic."""
        return "2B4B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for device wearing position."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="Other"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="Chest"),
            CharacteristicTestData(input_data=bytearray([2]), expected_value=2, description="Wrist"),
        ]

    # === Device Wearing Position-Specific Tests ===

    @pytest.mark.parametrize(
        "position_value,description",
        [
            (0, "Other"),
            (1, "Chest"),
            (2, "Wrist"),
            (3, "Finger"),
            (4, "Hand"),
            (5, "Ear"),
            (6, "Foot"),
        ],
    )
    def test_device_wearing_position_values(
        self, characteristic: DeviceWearingPositionCharacteristic, position_value: int, description: str
    ) -> None:
        """Test device wearing position with various valid values."""
        data = bytearray([position_value])
        result = characteristic.decode_value(data)
        assert result == position_value

    def test_device_wearing_position_boundary_values(self, characteristic: DeviceWearingPositionCharacteristic) -> None:
        """Test device wearing position boundary values."""
        # Test minimum value (0)
        result = characteristic.decode_value(bytearray([0]))
        assert result == 0

        # Test maximum value (255)
        result = characteristic.decode_value(bytearray([255]))
        assert result == 255
