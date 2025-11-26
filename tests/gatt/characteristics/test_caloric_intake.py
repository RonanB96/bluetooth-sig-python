"""Tests for Caloric Intake characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CaloricIntakeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCaloricIntakeCharacteristic(CommonCharacteristicTests):
    """Test suite for Caloric Intake characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds caloric intake-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> CaloricIntakeCharacteristic:
        """Return a Caloric Intake characteristic instance."""
        return CaloricIntakeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Caloric Intake characteristic."""
        return "2B50"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for caloric intake."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0, description="Zero calories"),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]), expected_value=1000, description="1000 calories"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=65535, description="Maximum calories"
            ),
        ]

    # === Caloric Intake-Specific Tests ===

    @pytest.mark.parametrize(
        "calories",
        [
            0,  # 0 calories
            500,  # 500 calories
            1000,  # 1000 calories
            2000,  # 2000 calories
            5000,  # 5000 calories
        ],
    )
    def test_caloric_intake_values(self, characteristic: CaloricIntakeCharacteristic, calories: int) -> None:
        """Test caloric intake with various valid values."""
        data = bytearray([calories & 0xFF, (calories >> 8) & 0xFF])
        result = characteristic.decode_value(data)
        assert result == calories

    def test_caloric_intake_boundary_values(self, characteristic: CaloricIntakeCharacteristic) -> None:
        """Test caloric intake boundary values."""
        # Test minimum value (0 calories)
        result = characteristic.decode_value(bytearray([0, 0]))
        assert result == 0

        # Test maximum value (65535 calories)
        result = characteristic.decode_value(bytearray([0xFF, 0xFF]))
        assert result == 65535
