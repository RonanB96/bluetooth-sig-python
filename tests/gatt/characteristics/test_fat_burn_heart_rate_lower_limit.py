"""Tests for Fat Burn Heart Rate Lower Limit characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FatBurnHeartRateLowerLimitCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFatBurnHeartRateLowerLimitCharacteristic(CommonCharacteristicTests):
    """Test suite for Fat Burn Heart Rate Lower Limit characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds fat burn heart rate lower limit-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> FatBurnHeartRateLowerLimitCharacteristic:
        """Return a Fat Burn Heart Rate Lower Limit characteristic instance."""
        return FatBurnHeartRateLowerLimitCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Fat Burn Heart Rate Lower Limit characteristic."""
        return "2A88"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for fat burn heart rate lower limit."""
        return [
            CharacteristicTestData(input_data=bytearray([100]), expected_value=100, description="100 BPM"),
            CharacteristicTestData(input_data=bytearray([120]), expected_value=120, description="120 BPM"),
            CharacteristicTestData(input_data=bytearray([140]), expected_value=140, description="140 BPM"),
        ]

    # === Fat Burn Heart Rate Lower Limit-Specific Tests ===

    @pytest.mark.parametrize(
        "heart_rate",
        [
            100,  # 100 BPM
            110,  # 110 BPM
            120,  # 120 BPM
            130,  # 130 BPM
            140,  # 140 BPM
        ],
    )
    def test_fat_burn_heart_rate_lower_limit_values(
        self, characteristic: FatBurnHeartRateLowerLimitCharacteristic, heart_rate: int
    ) -> None:
        """Test fat burn heart rate lower limit with various valid values."""
        data = bytearray([heart_rate])
        result = characteristic.parse_value(data)
        assert result == heart_rate

    def test_fat_burn_heart_rate_lower_limit_boundary_values(
        self, characteristic: FatBurnHeartRateLowerLimitCharacteristic
    ) -> None:
        """Test fat burn heart rate lower limit boundary values."""
        # Test minimum value (0 BPM)
        result = characteristic.parse_value(bytearray([0]))
        assert result == 0

        # Test maximum value (255 BPM)
        result = characteristic.parse_value(bytearray([255]))
        assert result == 255
