"""Tests for Heart Rate Max characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HeartRateMaxCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHeartRateMaxCharacteristic(CommonCharacteristicTests):
    """Test suite for Heart Rate Max characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds heart rate max-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> HeartRateMaxCharacteristic:
        """Return a Heart Rate Max characteristic instance."""
        return HeartRateMaxCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Heart Rate Max characteristic."""
        return "2A8D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for heart rate max."""
        return [
            CharacteristicTestData(input_data=bytearray([150]), expected_value=150, description="150 bpm"),
            CharacteristicTestData(input_data=bytearray([180]), expected_value=180, description="180 bpm"),
            CharacteristicTestData(input_data=bytearray([200]), expected_value=200, description="200 bpm"),
        ]

    # === Heart Rate Max-Specific Tests ===

    @pytest.mark.parametrize(
        "heart_rate_max",
        [
            120,  # Low max HR
            160,  # Average max HR
            190,  # High max HR
            220,  # Very high max HR
        ],
    )
    def test_heart_rate_max_values(self, characteristic: HeartRateMaxCharacteristic, heart_rate_max: int) -> None:
        """Test heart rate max with various valid values."""
        data = bytearray([heart_rate_max])
        result = characteristic.parse_value(data)
        assert result.value == heart_rate_max

    def test_heart_rate_max_boundary_values(self, characteristic: HeartRateMaxCharacteristic) -> None:
        """Test heart rate max boundary values."""
        # Test minimum (0 bpm)
        result = characteristic.parse_value(bytearray([0]))
        assert result.value == 0

        # Test maximum (255 bpm)
        result = characteristic.parse_value(bytearray([255]))
        assert result.value == 255
