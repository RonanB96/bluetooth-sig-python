"""Tests for VO2 Max characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import VO2MaxCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVO2MaxCharacteristic(CommonCharacteristicTests):
    """Test suite for VO2 Max characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds VO2 max-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> VO2MaxCharacteristic:
        """Return a VO2 Max characteristic instance."""
        return VO2MaxCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for VO2 Max characteristic."""
        return "2A96"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for VO2 max."""
        return [
            CharacteristicTestData(input_data=bytearray([30]), expected_value=30, description="30 ml/kg/min"),
            CharacteristicTestData(input_data=bytearray([45]), expected_value=45, description="45 ml/kg/min"),
            CharacteristicTestData(input_data=bytearray([60]), expected_value=60, description="60 ml/kg/min"),
        ]

    # === VO2 Max-Specific Tests ===

    @pytest.mark.parametrize(
        "vo2_max",
        [
            20,  # Poor fitness
            35,  # Average fitness
            50,  # Good fitness
            70,  # Excellent fitness
        ],
    )
    def test_vo2_max_values(self, characteristic: VO2MaxCharacteristic, vo2_max: int) -> None:
        """Test VO2 max with various valid values."""
        data = bytearray([vo2_max])
        result = characteristic.decode_value(data)
        assert result == vo2_max

    def test_vo2_max_boundary_values(self, characteristic: VO2MaxCharacteristic) -> None:
        """Test VO2 max boundary values."""
        # Test minimum (0)
        result = characteristic.decode_value(bytearray([0]))
        assert result == 0

        # Test maximum (255)
        result = characteristic.decode_value(bytearray([255]))
        assert result == 255
