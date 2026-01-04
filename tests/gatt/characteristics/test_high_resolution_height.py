"""Tests for High Resolution Height characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HighResolutionHeightCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHighResolutionHeightCharacteristic(CommonCharacteristicTests):
    """Test suite for High Resolution Height characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds high resolution height-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> HighResolutionHeightCharacteristic:
        """Return a High Resolution Height characteristic instance."""
        return HighResolutionHeightCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for High Resolution Height characteristic."""
        return "2B47"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for high resolution height."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0.0, description="Zero height"),
            CharacteristicTestData(input_data=bytearray([0xE8, 0x03]), expected_value=10.0, description="10 cm height"),
            CharacteristicTestData(input_data=bytearray([0xD0, 0x07]), expected_value=20.0, description="20 cm height"),
        ]

    # === High Resolution Height-Specific Tests ===

    @pytest.mark.parametrize(
        "raw_value,expected_height",
        [
            (0, 0.0),  # 0 cm
            (10000, 100.0),  # 100 cm
            (20000, 200.0),  # 200 cm
            (17500, 175.0),  # 175 cm
        ],
    )
    def test_high_resolution_height_values(
        self, characteristic: HighResolutionHeightCharacteristic, raw_value: int, expected_height: float
    ) -> None:
        """Test high resolution height with various valid values."""
        data = bytearray([raw_value & 0xFF, (raw_value >> 8) & 0xFF])
        result = characteristic.parse_value(data)
        assert result == expected_height

    def test_high_resolution_height_boundary_values(self, characteristic: HighResolutionHeightCharacteristic) -> None:
        """Test high resolution height boundary values."""
        # Test minimum value (0 cm)
        result = characteristic.parse_value(bytearray([0, 0]))
        assert result == 0.0

        # Test maximum value (655.35 cm)
        result = characteristic.parse_value(bytearray([0xFF, 0xFF]))
        assert result == 655.35
