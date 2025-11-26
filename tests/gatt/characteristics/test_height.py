"""Tests for Height characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HeightCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHeightCharacteristic(CommonCharacteristicTests):
    """Test suite for Height characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds height-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> HeightCharacteristic:
        """Return a Height characteristic instance."""
        return HeightCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Height characteristic."""
        return "2A8E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for height."""
        return [
            CharacteristicTestData(input_data=bytearray([0x74, 0x40]), expected_value=165.0, description="165.0 cm"),
            CharacteristicTestData(input_data=bytearray([0x5C, 0x44]), expected_value=175.0, description="175.0 cm"),
            CharacteristicTestData(input_data=bytearray([0x44, 0x48]), expected_value=185.0, description="185.0 cm"),
        ]

    # === Height-Specific Tests ===

    @pytest.mark.parametrize(
        "height_cm",
        [
            150.0,  # Short
            170.0,  # Average
            190.0,  # Tall
            220.0,  # Very tall
        ],
    )
    def test_height_values(self, characteristic: HeightCharacteristic, height_cm: float) -> None:
        """Test height with various valid values."""
        # Convert cm to scaled uint16 (height / 0.01)
        scaled_value = int(height_cm / 0.01)
        data = bytearray([scaled_value & 0xFF, (scaled_value >> 8) & 0xFF])
        result = characteristic.decode_value(data)
        assert abs(result - height_cm) < 0.01  # Allow small floating point error

    def test_height_boundary_values(self, characteristic: HeightCharacteristic) -> None:
        """Test height boundary values."""
        # Test minimum height (0 cm)
        result = characteristic.decode_value(bytearray([0, 0]))
        assert result == 0.0

        # Test maximum height (655.35 cm)
        result = characteristic.decode_value(bytearray([0xFF, 0xFF]))
        assert abs(result - 655.35) < 0.01
