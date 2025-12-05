"""Tests for Four Zone Heart Rate Limits characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FourZoneHeartRateLimitsCharacteristic
from bluetooth_sig.gatt.characteristics.four_zone_heart_rate_limits import FourZoneHeartRateLimitsData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFourZoneHeartRateLimitsCharacteristic(CommonCharacteristicTests):
    """Test suite for Four Zone Heart Rate Limits characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds four zone heart rate limits-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> FourZoneHeartRateLimitsCharacteristic:
        """Return a Four Zone Heart Rate Limits characteristic instance."""
        return FourZoneHeartRateLimitsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Four Zone Heart Rate Limits characteristic."""
        return "2B4C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for four zone heart rate limits."""
        return [
            CharacteristicTestData(
                input_data=bytearray([80, 100, 120]),
                expected_value=FourZoneHeartRateLimitsData(
                    light_moderate_limit=80, moderate_hard_limit=100, hard_maximum_limit=120
                ),
                description="80/100/120 BPM limits",
            ),
            CharacteristicTestData(
                input_data=bytearray([90, 120, 150]),
                expected_value=FourZoneHeartRateLimitsData(
                    light_moderate_limit=90, moderate_hard_limit=120, hard_maximum_limit=150
                ),
                description="90/120/150 BPM limits",
            ),
        ]

    # === Four Zone Heart Rate Limits-Specific Tests ===

    @pytest.mark.parametrize(
        "light_limit,moderate_limit,hard_limit",
        [
            (80, 100, 120),  # 80/100/120 BPM
            (90, 120, 150),  # 90/120/150 BPM
            (100, 140, 180),  # 100/140/180 BPM
        ],
    )
    def test_four_zone_heart_rate_limits_values(
        self,
        characteristic: FourZoneHeartRateLimitsCharacteristic,
        light_limit: int,
        moderate_limit: int,
        hard_limit: int,
    ) -> None:
        """Test four zone heart rate limits with various valid values."""
        data = bytearray([light_limit, moderate_limit, hard_limit])
        result = characteristic.decode_value(data)
        expected = FourZoneHeartRateLimitsData(
            light_moderate_limit=light_limit, moderate_hard_limit=moderate_limit, hard_maximum_limit=hard_limit
        )
        assert result == expected

    def test_four_zone_heart_rate_limits_boundary_values(
        self, characteristic: FourZoneHeartRateLimitsCharacteristic
    ) -> None:
        """Test four zone heart rate limits boundary values."""
        # Test minimum values (0 BPM)
        result = characteristic.decode_value(bytearray([0, 0, 0]))
        expected = FourZoneHeartRateLimitsData(light_moderate_limit=0, moderate_hard_limit=0, hard_maximum_limit=0)
        assert result == expected

        # Test maximum values (255 BPM)
        result = characteristic.decode_value(bytearray([255, 255, 255]))
        expected = FourZoneHeartRateLimitsData(
            light_moderate_limit=255, moderate_hard_limit=255, hard_maximum_limit=255
        )
        assert result == expected
