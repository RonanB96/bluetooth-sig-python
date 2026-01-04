"""Tests for Five Zone Heart Rate Limits characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FiveZoneHeartRateLimitsCharacteristic
from bluetooth_sig.gatt.characteristics.five_zone_heart_rate_limits import FiveZoneHeartRateLimitsData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFiveZoneHeartRateLimitsCharacteristic(CommonCharacteristicTests):
    """Test suite for Five Zone Heart Rate Limits characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds five zone heart rate limits-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> FiveZoneHeartRateLimitsCharacteristic:
        """Return a Five Zone Heart Rate Limits characteristic instance."""
        return FiveZoneHeartRateLimitsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Five Zone Heart Rate Limits characteristic."""
        return "2A8B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for five zone heart rate limits."""
        return [
            CharacteristicTestData(
                input_data=bytearray([70, 80, 100, 120]),
                expected_value=FiveZoneHeartRateLimitsData(
                    very_light_light_limit=70, light_moderate_limit=80, moderate_hard_limit=100, hard_maximum_limit=120
                ),
                description="70/80/100/120 BPM limits",
            ),
            CharacteristicTestData(
                input_data=bytearray([80, 90, 120, 150]),
                expected_value=FiveZoneHeartRateLimitsData(
                    very_light_light_limit=80, light_moderate_limit=90, moderate_hard_limit=120, hard_maximum_limit=150
                ),
                description="80/90/120/150 BPM limits",
            ),
        ]

    # === Five Zone Heart Rate Limits-Specific Tests ===

    @pytest.mark.parametrize(
        "limits",
        [
            (70, 80, 100, 120),  # 70/80/100/120 BPM
            (80, 90, 120, 150),  # 80/90/120/150 BPM
            (90, 110, 140, 180),  # 90/110/140/180 BPM
        ],
    )
    def test_five_zone_heart_rate_limits_values(
        self,
        characteristic: FiveZoneHeartRateLimitsCharacteristic,
        limits: tuple[int, int, int, int],
    ) -> None:
        """Test five zone heart rate limits with various valid values."""
        very_light_limit, light_limit, moderate_limit, hard_limit = limits
        data = bytearray([very_light_limit, light_limit, moderate_limit, hard_limit])
        result = characteristic.parse_value(data)
        expected = FiveZoneHeartRateLimitsData(
            very_light_light_limit=very_light_limit,
            light_moderate_limit=light_limit,
            moderate_hard_limit=moderate_limit,
            hard_maximum_limit=hard_limit,
        )
        assert result.value == expected

    def test_five_zone_heart_rate_limits_boundary_values(
        self, characteristic: FiveZoneHeartRateLimitsCharacteristic
    ) -> None:
        """Test five zone heart rate limits boundary values."""
        # Test minimum values (0 BPM)
        result = characteristic.parse_value(bytearray([0, 0, 0, 0]))
        expected = FiveZoneHeartRateLimitsData(
            very_light_light_limit=0, light_moderate_limit=0, moderate_hard_limit=0, hard_maximum_limit=0
        )
        assert result.value == expected

        # Test maximum values (255 BPM)
        result = characteristic.parse_value(bytearray([255, 255, 255, 255]))
        expected = FiveZoneHeartRateLimitsData(
            very_light_light_limit=255, light_moderate_limit=255, moderate_hard_limit=255, hard_maximum_limit=255
        )
        assert result.value == expected
