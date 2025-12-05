"""Tests for Maximum Recommended Heart Rate characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import MaximumRecommendedHeartRateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMaximumRecommendedHeartRateCharacteristic(CommonCharacteristicTests):
    """Test suite for Maximum Recommended Heart Rate characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds maximum recommended heart rate-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> MaximumRecommendedHeartRateCharacteristic:
        """Return a Maximum Recommended Heart Rate characteristic instance."""
        return MaximumRecommendedHeartRateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Maximum Recommended Heart Rate characteristic."""
        return "2A91"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for maximum recommended heart rate."""
        return [
            CharacteristicTestData(input_data=bytearray([140]), expected_value=140, description="140 bpm"),
            CharacteristicTestData(input_data=bytearray([160]), expected_value=160, description="160 bpm"),
            CharacteristicTestData(input_data=bytearray([180]), expected_value=180, description="180 bpm"),
        ]

    # === Maximum Recommended Heart Rate-Specific Tests ===

    @pytest.mark.parametrize(
        "hr",
        [
            130,  # Conservative max
            150,  # Moderate max
            170,  # Aggressive max
            190,  # Very aggressive max
        ],
    )
    def test_max_rec_hr_values(self, characteristic: MaximumRecommendedHeartRateCharacteristic, hr: int) -> None:
        """Test maximum recommended heart rate with various valid values."""
        data = bytearray([hr])
        result = characteristic.decode_value(data)
        assert result == hr

    def test_max_rec_hr_boundary_values(self, characteristic: MaximumRecommendedHeartRateCharacteristic) -> None:
        """Test maximum recommended heart rate boundary values."""
        # Test minimum (0 bpm)
        result = characteristic.decode_value(bytearray([0]))
        assert result == 0

        # Test maximum (255 bpm)
        result = characteristic.decode_value(bytearray([255]))
        assert result == 255
