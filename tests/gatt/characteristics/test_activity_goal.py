"""Tests for Activity Goal characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ActivityGoalCharacteristic
from bluetooth_sig.gatt.characteristics.activity_goal import ActivityGoalData, ActivityGoalPresenceFlags
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestActivityGoalCharacteristic(CommonCharacteristicTests):
    """Test suite for Activity Goal characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds activity goal-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> ActivityGoalCharacteristic:
        """Return an Activity Goal characteristic instance."""
        return ActivityGoalCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Activity Goal characteristic."""
        return "2B4E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for activity goal."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),  # Presence flags + total energy expenditure
                expected_value=ActivityGoalData(
                    presence_flags=ActivityGoalPresenceFlags.TOTAL_ENERGY_EXPENDITURE,
                    total_energy_expenditure=0,
                    normal_walking_steps=None,
                    intensity_steps=None,
                    floor_steps=None,
                    distance=None,
                    duration_normal_walking=None,
                    duration_intensity_walking=None,
                ),
                description="Only total energy expenditure present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00]),  # No fields present
                expected_value=ActivityGoalData(
                    presence_flags=ActivityGoalPresenceFlags(0),
                    total_energy_expenditure=None,
                    normal_walking_steps=None,
                    intensity_steps=None,
                    floor_steps=None,
                    distance=None,
                    duration_normal_walking=None,
                    duration_intensity_walking=None,
                ),
                description="No fields present",
            ),
        ]

    # === Activity Goal-Specific Tests ===

    def test_activity_goal_total_energy_expenditure_only(self, characteristic: ActivityGoalCharacteristic) -> None:
        """Test activity goal with only total energy expenditure present."""
        # Presence flags: 0x01 (bit 0 set), Total energy expenditure: 500 kcal
        data = bytearray([0x01, 0xF4, 0x01])  # 0x01F4 = 500
        result = characteristic.parse_value(data)
        expected = ActivityGoalData(
            presence_flags=ActivityGoalPresenceFlags.TOTAL_ENERGY_EXPENDITURE,
            total_energy_expenditure=500,
            normal_walking_steps=None,
            intensity_steps=None,
            floor_steps=None,
            distance=None,
            duration_normal_walking=None,
            duration_intensity_walking=None,
        )
        assert result == expected

    def test_activity_goal_multiple_fields(self, characteristic: ActivityGoalCharacteristic) -> None:
        """Test activity goal with multiple fields present."""
        # Presence flags: 0x03 (bits 0 and 1 set)
        # Total energy expenditure: 1000 kcal, Normal walking steps: 5000
        data = bytearray([0x03, 0xE8, 0x03, 0x88, 0x13, 0x00])  # 0x03E8 = 1000, 0x001388 = 5000
        result = characteristic.parse_value(data)
        expected = ActivityGoalData(
            presence_flags=ActivityGoalPresenceFlags.TOTAL_ENERGY_EXPENDITURE
            | ActivityGoalPresenceFlags.NORMAL_WALKING_STEPS,
            total_energy_expenditure=1000,
            normal_walking_steps=5000,
            intensity_steps=None,
            floor_steps=None,
            distance=None,
            duration_normal_walking=None,
            duration_intensity_walking=None,
        )
        assert result == expected

    def test_activity_goal_all_fields(self, characteristic: ActivityGoalCharacteristic) -> None:
        """Test activity goal with all fields present."""
        # Presence flags: 0x7F (all defined bits set)
        # All fields present with sample values
        data = bytearray(
            [
                0x7F,  # Presence flags
                0xE8,
                0x03,  # Total energy expenditure: 1000
                0x88,
                0x13,
                0x00,  # Normal walking steps: 5000
                0x44,
                0x0A,
                0x00,  # Intensity steps: 2628
                0x22,
                0x05,
                0x00,  # Floor steps: 1314
                0x00,
                0x02,
                0x00,  # Distance: 512
                0x80,
                0x0C,
                0x00,  # Duration normal walking: 3200
                0x40,
                0x06,
                0x00,  # Duration intensity walking: 1600
            ]
        )
        result = characteristic.parse_value(data)
        expected = ActivityGoalData(
            presence_flags=ActivityGoalPresenceFlags.TOTAL_ENERGY_EXPENDITURE
            | ActivityGoalPresenceFlags.NORMAL_WALKING_STEPS
            | ActivityGoalPresenceFlags.INTENSITY_STEPS
            | ActivityGoalPresenceFlags.FLOOR_STEPS
            | ActivityGoalPresenceFlags.DISTANCE
            | ActivityGoalPresenceFlags.DURATION_NORMAL_WALKING
            | ActivityGoalPresenceFlags.DURATION_INTENSITY_WALKING,
            total_energy_expenditure=1000,
            normal_walking_steps=5000,
            intensity_steps=2628,
            floor_steps=1314,
            distance=512,
            duration_normal_walking=3200,
            duration_intensity_walking=1600,
        )
        assert result == expected

    def test_activity_goal_no_fields(self, characteristic: ActivityGoalCharacteristic) -> None:
        """Test activity goal with no fields present."""
        data = bytearray([0x00])  # Presence flags only, no fields
        result = characteristic.parse_value(data)
        expected = ActivityGoalData(
            presence_flags=ActivityGoalPresenceFlags(0),
            total_energy_expenditure=None,
            normal_walking_steps=None,
            intensity_steps=None,
            floor_steps=None,
            distance=None,
            duration_normal_walking=None,
            duration_intensity_walking=None,
        )
        assert result == expected
