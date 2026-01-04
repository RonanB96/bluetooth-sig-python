"""Tests for Three Zone Heart Rate Limits characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ThreeZoneHeartRateLimitsCharacteristic
from bluetooth_sig.gatt.characteristics.three_zone_heart_rate_limits import ThreeZoneHeartRateLimitsData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestThreeZoneHeartRateLimitsCharacteristic(CommonCharacteristicTests):
    """Test suite for Three Zone Heart Rate Limits characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds three zone heart rate limits-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> ThreeZoneHeartRateLimitsCharacteristic:
        """Return a Three Zone Heart Rate Limits characteristic instance."""
        return ThreeZoneHeartRateLimitsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Three Zone Heart Rate Limits characteristic."""
        return "2A94"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for three zone heart rate limits."""
        return [
            CharacteristicTestData(
                input_data=bytearray([80, 100]),
                expected_value=ThreeZoneHeartRateLimitsData(light_moderate_limit=80, moderate_hard_limit=100),
                description="80/100 BPM limits",
            ),
            CharacteristicTestData(
                input_data=bytearray([90, 120]),
                expected_value=ThreeZoneHeartRateLimitsData(light_moderate_limit=90, moderate_hard_limit=120),
                description="90/120 BPM limits",
            ),
        ]

    # === Three Zone Heart Rate Limits-Specific Tests ===

    @pytest.mark.parametrize(
        "light_limit,hard_limit",
        [
            (80, 100),  # 80/100 BPM
            (90, 120),  # 90/120 BPM
            (100, 140),  # 100/140 BPM
        ],
    )
    def test_three_zone_heart_rate_limits_values(
        self, characteristic: ThreeZoneHeartRateLimitsCharacteristic, light_limit: int, hard_limit: int
    ) -> None:
        """Test three zone heart rate limits with various valid values."""
        data = bytearray([light_limit, hard_limit])
        result = characteristic.parse_value(data)
        expected = ThreeZoneHeartRateLimitsData(light_moderate_limit=light_limit, moderate_hard_limit=hard_limit)
        assert result.value == expected

    def test_three_zone_heart_rate_limits_boundary_values(
        self, characteristic: ThreeZoneHeartRateLimitsCharacteristic
    ) -> None:
        """Test three zone heart rate limits boundary values."""
        # Test minimum values (0 BPM)
        result = characteristic.parse_value(bytearray([0, 0]))
        expected = ThreeZoneHeartRateLimitsData(light_moderate_limit=0, moderate_hard_limit=0)
        assert result.value == expected

        # Test maximum values (255 BPM)
        result = characteristic.parse_value(bytearray([255, 255]))
        expected = ThreeZoneHeartRateLimitsData(light_moderate_limit=255, moderate_hard_limit=255)
        assert result.value == expected
