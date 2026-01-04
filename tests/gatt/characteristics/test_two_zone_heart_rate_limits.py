"""Tests for Two Zone Heart Rate Limits characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TwoZoneHeartRateLimitsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTwoZoneHeartRateLimitsCharacteristic(CommonCharacteristicTests):
    """Test suite for Two Zone Heart Rate Limits characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds two zone heart rate limits-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> TwoZoneHeartRateLimitsCharacteristic:
        """Return a Two Zone Heart Rate Limits characteristic instance."""
        return TwoZoneHeartRateLimitsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Two Zone Heart Rate Limits characteristic."""
        return "2A95"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for two zone heart rate limits."""
        return [
            CharacteristicTestData(input_data=bytearray([70]), expected_value=70, description="70 BPM"),
            CharacteristicTestData(input_data=bytearray([90]), expected_value=90, description="90 BPM"),
            CharacteristicTestData(input_data=bytearray([110]), expected_value=110, description="110 BPM"),
        ]

    # === Two Zone Heart Rate Limits-Specific Tests ===

    @pytest.mark.parametrize(
        "heart_rate",
        [
            70,  # 70 BPM
            80,  # 80 BPM
            90,  # 90 BPM
            100,  # 100 BPM
            110,  # 110 BPM
        ],
    )
    def test_two_zone_heart_rate_limits_values(
        self, characteristic: TwoZoneHeartRateLimitsCharacteristic, heart_rate: int
    ) -> None:
        """Test two zone heart rate limits with various valid values."""
        data = bytearray([heart_rate])
        result = characteristic.parse_value(data)
        assert result.value == heart_rate

    def test_two_zone_heart_rate_limits_boundary_values(
        self, characteristic: TwoZoneHeartRateLimitsCharacteristic
    ) -> None:
        """Test two zone heart rate limits boundary values."""
        # Test minimum value (0 BPM)
        result = characteristic.parse_value(bytearray([0]))
        assert result.value == 0

        # Test maximum value (255 BPM)
        result = characteristic.parse_value(bytearray([255]))
        assert result.value == 255
