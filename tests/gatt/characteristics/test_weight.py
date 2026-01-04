"""Tests for Weight characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import WeightCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestWeightCharacteristic(CommonCharacteristicTests):
    """Test suite for Weight characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds weight-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> WeightCharacteristic:
        """Return a Weight characteristic instance."""
        return WeightCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Weight characteristic."""
        return "2A98"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for weight."""
        return [
            CharacteristicTestData(input_data=bytearray([0x10, 0x27]), expected_value=50.0, description="50.0 kg"),
            CharacteristicTestData(input_data=bytearray([0x98, 0x3A]), expected_value=75.0, description="75.0 kg"),
            CharacteristicTestData(input_data=bytearray([0x20, 0x4E]), expected_value=100.0, description="100.0 kg"),
        ]

    # === Weight-Specific Tests ===

    @pytest.mark.parametrize(
        "weight_kg",
        [
            50.0,  # Average weight
            75.0,  # Overweight
            100.0,  # Heavy weight
            150.0,  # Very heavy
        ],
    )
    def test_weight_values(self, characteristic: WeightCharacteristic, weight_kg: float) -> None:
        """Test weight with various valid values."""
        # Convert kg to scaled uint16 (weight / 0.005)
        scaled_value = int(weight_kg / 0.005)
        data = bytearray([scaled_value & 0xFF, (scaled_value >> 8) & 0xFF])
        result = characteristic.parse_value(data)

        assert result is not None
        assert abs(result - weight_kg) < 0.01  # Allow small floating point error

    def test_weight_boundary_values(self, characteristic: WeightCharacteristic) -> None:
        """Test weight boundary values."""
        # Test minimum weight (0 kg)
        result = characteristic.parse_value(bytearray([0, 0]))

        assert result is not None
        assert result == 0.0

        # Test maximum weight (327.675 kg)
        result = characteristic.parse_value(bytearray([0xFF, 0xFF]))

        assert result is not None
        assert abs(result - 327.675) < 0.01
