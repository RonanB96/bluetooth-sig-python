"""Tests for Resting Heart Rate characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import RestingHeartRateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRestingHeartRateCharacteristic(CommonCharacteristicTests):
    """Test suite for Resting Heart Rate characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds resting heart rate-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> RestingHeartRateCharacteristic:
        """Return a Resting Heart Rate characteristic instance."""
        return RestingHeartRateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Resting Heart Rate characteristic."""
        return "2A92"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for resting heart rate."""
        return [
            CharacteristicTestData(input_data=bytearray([60]), expected_value=60, description="60 bpm"),
            CharacteristicTestData(input_data=bytearray([70]), expected_value=70, description="70 bpm"),
            CharacteristicTestData(input_data=bytearray([80]), expected_value=80, description="80 bpm"),
        ]

    # === Resting Heart Rate-Specific Tests ===

    @pytest.mark.parametrize(
        "resting_hr",
        [
            50,  # Very low RHR
            65,  # Good RHR
            75,  # Average RHR
            90,  # High RHR
        ],
    )
    def test_resting_heart_rate_values(self, characteristic: RestingHeartRateCharacteristic, resting_hr: int) -> None:
        """Test resting heart rate with various valid values."""
        data = bytearray([resting_hr])
        result = characteristic.decode_value(data)
        assert result == resting_hr

    def test_resting_heart_rate_boundary_values(self, characteristic: RestingHeartRateCharacteristic) -> None:
        """Test resting heart rate boundary values."""
        # Test minimum (0 bpm)
        result = characteristic.decode_value(bytearray([0]))
        assert result == 0

        # Test maximum (255 bpm)
        result = characteristic.decode_value(bytearray([255]))
        assert result == 255
