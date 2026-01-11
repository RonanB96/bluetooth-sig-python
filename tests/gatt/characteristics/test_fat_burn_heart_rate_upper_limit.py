"""Tests for Fat Burn Heart Rate Upper Limit characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FatBurnHeartRateUpperLimitCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFatBurnHeartRateUpperLimitCharacteristic(CommonCharacteristicTests):
    """Test suite for Fat Burn Heart Rate Upper Limit characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds fat burn heart rate upper limit-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> FatBurnHeartRateUpperLimitCharacteristic:
        """Return a Fat Burn Heart Rate Upper Limit characteristic instance."""
        return FatBurnHeartRateUpperLimitCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Fat Burn Heart Rate Upper Limit characteristic."""
        return "2A89"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for fat burn heart rate upper limit."""
        return [
            CharacteristicTestData(input_data=bytearray([120]), expected_value=120, description="120 BPM"),
            CharacteristicTestData(input_data=bytearray([140]), expected_value=140, description="140 BPM"),
            CharacteristicTestData(input_data=bytearray([160]), expected_value=160, description="160 BPM"),
        ]

    # === Fat Burn Heart Rate Upper Limit-Specific Tests ===

    @pytest.mark.parametrize(
        "heart_rate",
        [
            120,  # 120 BPM
            130,  # 130 BPM
            140,  # 140 BPM
            150,  # 150 BPM
            160,  # 160 BPM
        ],
    )
    def test_fat_burn_heart_rate_upper_limit_values(
        self, characteristic: FatBurnHeartRateUpperLimitCharacteristic, heart_rate: int
    ) -> None:
        """Test fat burn heart rate upper limit with various valid values."""
        data = bytearray([heart_rate])
        result = characteristic.parse_value(data)
        assert result == heart_rate

    def test_fat_burn_heart_rate_upper_limit_boundary_values(
        self, characteristic: FatBurnHeartRateUpperLimitCharacteristic
    ) -> None:
        """Test fat burn heart rate upper limit boundary values."""
        # Test minimum value (0 BPM)
        result = characteristic.parse_value(bytearray([0]))
        assert result == 0

        # Test maximum value (255 BPM)
        result = characteristic.parse_value(bytearray([255]))
        assert result == 255
