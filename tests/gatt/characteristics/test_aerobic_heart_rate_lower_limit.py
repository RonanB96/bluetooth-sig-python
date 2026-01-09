"""Tests for Aerobic Heart Rate Lower Limit characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AerobicHeartRateLowerLimitCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAerobicHeartRateLowerLimitCharacteristic(CommonCharacteristicTests):
    """Test suite for Aerobic Heart Rate Lower Limit characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds aerobic heart rate lower limit-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> AerobicHeartRateLowerLimitCharacteristic:
        """Return an Aerobic Heart Rate Lower Limit characteristic instance."""
        return AerobicHeartRateLowerLimitCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Aerobic Heart Rate Lower Limit characteristic."""
        return "2A7E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for aerobic heart rate lower limit."""
        return [
            CharacteristicTestData(input_data=bytearray([60]), expected_value=60, description="60 BPM"),
            CharacteristicTestData(input_data=bytearray([80]), expected_value=80, description="80 BPM"),
            CharacteristicTestData(input_data=bytearray([100]), expected_value=100, description="100 BPM"),
        ]

    # === Aerobic Heart Rate Lower Limit-Specific Tests ===

    @pytest.mark.parametrize(
        "heart_rate",
        [
            60,  # 60 BPM
            70,  # 70 BPM
            80,  # 80 BPM
            90,  # 90 BPM
            100,  # 100 BPM
        ],
    )
    def test_aerobic_heart_rate_lower_limit_values(
        self, characteristic: AerobicHeartRateLowerLimitCharacteristic, heart_rate: int
    ) -> None:
        """Test aerobic heart rate lower limit with various valid values."""
        data = bytearray([heart_rate])
        result = characteristic.parse_value(data)
        assert result == heart_rate

    def test_aerobic_heart_rate_lower_limit_boundary_values(
        self, characteristic: AerobicHeartRateLowerLimitCharacteristic
    ) -> None:
        """Test aerobic heart rate lower limit boundary values."""
        # Test minimum value (0 BPM)
        result = characteristic.parse_value(bytearray([0]))
        assert result == 0

        # Test maximum value (255 BPM)
        result = characteristic.parse_value(bytearray([255]))
        assert result == 255
