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
        """Return valid test data for high resolution height.

        GSS: uint16, M=1 d=-4 b=0 (0.0001 m = 0.1 mm resolution).
        """
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0.0, description="Zero height"),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),  # 1000 * 0.0001 = 0.1 m
                expected_value=0.1,
                description="0.1 m (100 mm)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xD0, 0x07]),  # 2000 * 0.0001 = 0.2 m
                expected_value=0.2,
                description="0.2 m (200 mm)",
            ),
        ]

    # === High Resolution Height-Specific Tests ===

    @pytest.mark.parametrize(
        "raw_value,expected_height",
        [
            (0, 0.0),  # 0 m
            (10000, 1.0),  # 10000 * 0.0001 = 1.0 m
            (20000, 2.0),  # 20000 * 0.0001 = 2.0 m
            (17500, 1.75),  # 17500 * 0.0001 = 1.75 m
        ],
    )
    def test_high_resolution_height_values(
        self, characteristic: HighResolutionHeightCharacteristic, raw_value: int, expected_height: float
    ) -> None:
        """Test high resolution height with various valid values."""
        data = bytearray([raw_value & 0xFF, (raw_value >> 8) & 0xFF])
        result = characteristic.parse_value(data)
        assert abs(result - expected_height) < 1e-9

    def test_high_resolution_height_boundary_values(self, characteristic: HighResolutionHeightCharacteristic) -> None:
        """Test high resolution height boundary values."""
        result = characteristic.parse_value(bytearray([0, 0]))
        assert result == 0.0

        # Max: 65535 * 0.0001 = 6.5535 m
        result = characteristic.parse_value(bytearray([0xFF, 0xFF]))
        assert abs(result - 6.5535) < 1e-9
