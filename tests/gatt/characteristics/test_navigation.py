"""Tests for Navigation characteristic."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics import NavigationCharacteristic
from bluetooth_sig.gatt.characteristics.navigation import (
    HeadingSource,
    NavigationData,
    NavigationFlags,
    NavigationIndicatorType,
)
from bluetooth_sig.types import PositionStatus
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestNavigationCharacteristic(CommonCharacteristicTests):
    """Test suite for Navigation characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds navigation-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> NavigationCharacteristic:
        """Return a Navigation characteristic instance."""
        return NavigationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Navigation characteristic."""
        return "2A68"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for navigation (bearing and heading)."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x5A, 0x00, 0x2D, 0x01]),  # bearing=90, heading=301
                expected_value=NavigationData(
                    flags=NavigationFlags(0),
                    bearing=0.9,  # 90 units of 0.01 degrees = 0.9 degrees
                    heading=3.01,  # 301 units of 0.01 degrees = 3.01 degrees
                    remaining_distance=None,
                    remaining_vertical_distance=None,
                    estimated_time_of_arrival=None,
                    position_status=PositionStatus.NO_POSITION,
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                    navigation_indicator_type=NavigationIndicatorType.TO_WAYPOINT,
                    waypoint_reached=False,
                    destination_reached=False,
                ),
                description="Navigation with bearing and heading",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0xB4, 0x00, 0x68, 0x01]),  # bearing=180, heading=360
                expected_value=NavigationData(
                    flags=NavigationFlags(0),
                    bearing=1.8,  # 180 units of 0.01 degrees = 1.8 degrees
                    heading=3.6,  # 360 units of 0.01 degrees = 3.6 degrees
                    remaining_distance=None,
                    remaining_vertical_distance=None,
                    estimated_time_of_arrival=None,
                    position_status=PositionStatus.NO_POSITION,
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                    navigation_indicator_type=NavigationIndicatorType.TO_WAYPOINT,
                    waypoint_reached=False,
                    destination_reached=False,
                ),
                description="Navigation with bearing 180 and heading 360",
            ),
        ]

    # === Navigation-Specific Tests ===
    @pytest.mark.parametrize(
        "data,expected",
        [
            # Basic: bearing and heading only
            (
                bytearray([0x00, 0x00, 0x5A, 0x00, 0x2D, 0x01]),
                NavigationData(
                    flags=NavigationFlags(0),
                    bearing=0.9,
                    heading=3.01,
                    remaining_distance=None,
                    remaining_vertical_distance=None,
                    estimated_time_of_arrival=None,
                    position_status=PositionStatus.NO_POSITION,
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                    navigation_indicator_type=NavigationIndicatorType.TO_WAYPOINT,
                    waypoint_reached=False,
                    destination_reached=False,
                ),
            ),
            # With remaining distance
            (
                bytearray([0x01, 0x00, 0x5A, 0x00, 0x2D, 0x01, 0x00, 0x00, 0x00]),
                NavigationData(
                    flags=NavigationFlags(0x0001),
                    bearing=0.9,
                    heading=3.01,
                    remaining_distance=0.0,
                    remaining_vertical_distance=None,
                    estimated_time_of_arrival=None,
                    position_status=PositionStatus.NO_POSITION,
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                    navigation_indicator_type=NavigationIndicatorType.TO_WAYPOINT,
                    waypoint_reached=False,
                    destination_reached=False,
                ),
            ),
            # With remaining vertical distance
            (
                bytearray([0x02, 0x00, 0x5A, 0x00, 0x2D, 0x01, 0x00, 0x00, 0x00]),
                NavigationData(
                    flags=NavigationFlags(0x0002),
                    bearing=0.9,
                    heading=3.01,
                    remaining_distance=None,
                    remaining_vertical_distance=0.0,
                    estimated_time_of_arrival=None,
                    position_status=PositionStatus.POSITION_OK,  # Bits 1-2 = 0b01 = 1
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                    navigation_indicator_type=NavigationIndicatorType.TO_WAYPOINT,
                    waypoint_reached=False,
                    destination_reached=False,
                ),
            ),
            # With ETA
            (
                bytearray([0x04, 0x00, 0x5A, 0x00, 0x2D, 0x01, 0xE7, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00]),
                NavigationData(
                    flags=NavigationFlags(0x0004),
                    bearing=0.9,
                    heading=3.01,
                    remaining_distance=None,
                    remaining_vertical_distance=None,
                    estimated_time_of_arrival=datetime(2023, 1, 1, 0, 0, 0),
                    position_status=PositionStatus.ESTIMATED_POSITION,  # Bits 1-2 = 0b10 = 2
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                    navigation_indicator_type=NavigationIndicatorType.TO_WAYPOINT,
                    waypoint_reached=False,
                    destination_reached=False,
                ),
            ),
            # All optional fields
            (
                bytearray(
                    [
                        0x07,
                        0x00,  # flags
                        0x5A,
                        0x00,  # bearing
                        0x2D,
                        0x01,  # heading
                        0x00,
                        0x00,
                        0x00,  # remaining_distance (3 bytes uint24)
                        0x00,
                        0x00,
                        0x00,  # remaining_vertical_distance (3 bytes sint24)
                        0xE7,
                        0x07,  # ETA year: 2023 (little-endian)
                        0x01,  # ETA month: 1
                        0x01,  # ETA day: 1
                        0x00,  # ETA hours: 0
                        0x00,  # ETA minutes: 0
                        0x00,  # ETA seconds: 0
                    ]
                ),
                NavigationData(
                    flags=NavigationFlags(0x0007),
                    bearing=0.9,
                    heading=3.01,
                    remaining_distance=0.0,
                    remaining_vertical_distance=0.0,
                    estimated_time_of_arrival=datetime(2023, 1, 1, 0, 0, 0),
                    position_status=PositionStatus.LAST_KNOWN_POSITION,  # Bits 1-2 = 0b11 = 3
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                    navigation_indicator_type=NavigationIndicatorType.TO_WAYPOINT,
                    waypoint_reached=False,
                    destination_reached=False,
                ),
            ),
        ],
    )
    def test_navigation_flag_combinations(
        self, characteristic: NavigationCharacteristic, data: bytearray, expected: NavigationData
    ) -> None:
        """Test navigation with various flag combinations."""
        result = characteristic.parse_value(data)
        assert result == expected

    def test_navigation_zero_values(self, characteristic: NavigationCharacteristic) -> None:
        """Test navigation with zero bearing and heading."""
        data = bytearray(
            [
                0x00,
                0x00,  # flags
                0x00,
                0x00,  # bearing (0.0 degrees)
                0x00,
                0x00,  # heading (0.0 degrees)
            ]
        )

        result = characteristic.parse_value(data)
        assert result.bearing == 0.0
        assert result.heading == 0.0

    def test_navigation_maximum_values(self, characteristic: NavigationCharacteristic) -> None:
        """Test navigation with maximum bearing and heading values."""
        data = bytearray(
            [
                0x00,
                0x00,  # flags
                0x9F,
                0x8C,  # bearing (359.99 degrees: 35999 * 0.01)
                0x9F,
                0x8C,  # heading (359.99 degrees: 35999 * 0.01)
            ]
        )

        result = characteristic.parse_value(data)
        assert result.bearing == 359.99
        assert result.heading == 359.99

    def test_navigation_boundary_values(self, characteristic: NavigationCharacteristic) -> None:
        """Test navigation boundary values."""
        # Test 359.99 degrees (maximum)
        data = bytearray([0x00, 0x00, 0x9F, 0x8C, 0x9F, 0x8C])
        result = characteristic.parse_value(data)
        assert result.bearing == 359.99
        assert result.heading == 359.99

        # Test 0 degrees (minimum)
        data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert result.bearing == 0.0
        assert result.heading == 0.0
