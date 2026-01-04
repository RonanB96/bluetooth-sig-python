"""Tests for Sedentary Interval Notification characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SedentaryIntervalNotificationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSedentaryIntervalNotificationCharacteristic(CommonCharacteristicTests):
    """Test suite for Sedentary Interval Notification characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds sedentary interval notification-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> SedentaryIntervalNotificationCharacteristic:
        """Return a Sedentary Interval Notification characteristic instance."""
        return SedentaryIntervalNotificationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Sedentary Interval Notification characteristic."""
        return "2B4F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for sedentary interval notification."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0, description="No notification"),
            CharacteristicTestData(input_data=bytearray([30, 0]), expected_value=30, description="30 minute interval"),
            CharacteristicTestData(input_data=bytearray([60, 0]), expected_value=60, description="60 minute interval"),
        ]

    # === Sedentary Interval Notification-Specific Tests ===

    @pytest.mark.parametrize(
        "interval_minutes",
        [
            0,  # No notification
            15,  # 15 minutes
            30,  # 30 minutes
            60,  # 60 minutes
            120,  # 2 hours
        ],
    )
    def test_sedentary_interval_notification_values(
        self, characteristic: SedentaryIntervalNotificationCharacteristic, interval_minutes: int
    ) -> None:
        """Test sedentary interval notification with various valid values."""
        data = bytearray([interval_minutes & 0xFF, (interval_minutes >> 8) & 0xFF])
        result = characteristic.parse_value(data)
        assert result.value == interval_minutes

    def test_sedentary_interval_notification_boundary_values(
        self, characteristic: SedentaryIntervalNotificationCharacteristic
    ) -> None:
        """Test sedentary interval notification boundary values."""
        # Test minimum value (0 minutes)
        result = characteristic.parse_value(bytearray([0, 0]))
        assert result.value == 0

        # Test maximum value (65535 minutes)
        result = characteristic.parse_value(bytearray([0xFF, 0xFF]))
        assert result.value == 65535
