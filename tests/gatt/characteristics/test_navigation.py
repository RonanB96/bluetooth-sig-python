"""Tests for Navigation characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import NavigationCharacteristic
from bluetooth_sig.gatt.characteristics.navigation import (
    HeadingSource,
    NavigationData,
    NavigationFlags,
    NavigationIndicatorType,
    PositionStatus,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestNavigationCharacteristic(CommonCharacteristicTests):
    """Test suite for Navigation characteristic.

    Inherits behavioral tests from CommonCharacteristicTests.
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
    def valid_test_data(self) -> CharacteristicTestData:
        """Return valid test data for navigation (bearing and heading)."""
        # Navigation data: flags(2) + bearing(2) + heading(2)
        data = bytearray(
            [
                0x00,
                0x00,  # flags (no optional fields)
                0x5A,
                0x00,  # bearing (90.0 degrees)
                0x2D,
                0x01,  # heading (301.0 degrees)
            ]
        )
        return CharacteristicTestData(
            input_data=data,
            expected_value=NavigationData(
                flags=NavigationFlags(0),
                bearing=0.9,  # 0x005A = 90 units of 0.01 degrees = 0.9 degrees
                heading=3.01,  # 0x012D = 301 units of 0.01 degrees = 3.01 degrees
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
        )

    # === Navigation-Specific Tests ===
    @pytest.mark.parametrize(
        "flags,data,expected",
        [
            # Basic: bearing and heading only
            (
                0x0000,
                bytearray([0x00, 0x00, 0x5A, 0x00, 0x2D, 0x01]),  # bearing=90.0, heading=301.0
                {
                    "bearing": 0.9,  # 90 * 0.01
                    "heading": 3.01,  # 301 * 0.01
                    "remaining_distance": None,
                    "remaining_vertical_distance": None,
                    "estimated_time_of_arrival": None,
                },
            ),
            # With remaining distance
            (
                0x0001,  # REMAINING_DISTANCE_PRESENT
                bytearray([0x01, 0x00, 0x5A, 0x00, 0x2D, 0x01, 0x00, 0x00, 0x00]),  # + distance=0
                {
                    "bearing": 0.9,
                    "heading": 3.01,
                    "remaining_distance": 0.0,
                    "remaining_vertical_distance": None,
                    "estimated_time_of_arrival": None,
                },
            ),
            # With remaining vertical distance
            (
                0x0002,  # REMAINING_VERTICAL_DISTANCE_PRESENT
                bytearray([0x02, 0x00, 0x5A, 0x00, 0x2D, 0x01, 0x00, 0x00, 0x00]),  # + vert_distance=0
                {
                    "bearing": 0.9,
                    "heading": 3.01,
                    "remaining_distance": None,
                    "remaining_vertical_distance": 0.0,
                    "estimated_time_of_arrival": None,
                },
            ),
            # With ETA
            (
                0x0004,  # ESTIMATED_TIME_OF_ARRIVAL_PRESENT
                bytearray(
                    [0x04, 0x00, 0x5A, 0x00, 0x2D, 0x01, 0xE7, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00]
                ),  # + 2023-01-01
                {
                    "bearing": 0.9,
                    "heading": 3.01,
                    "remaining_distance": None,
                    "remaining_vertical_distance": None,
                    "estimated_time_of_arrival": "2023-01-01T00:00:00",
                },
            ),
            # All optional fields
            (
                0x0007,  # All optional fields present
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
                        0x00,  # remaining_distance
                        0x00,
                        0x00,
                        0x00,  # remaining_vertical_distance
                        0xE7,
                        0x07,
                        0x01,
                        0x01,
                        0x00,
                        0x00,
                        0x00,  # ETA
                    ]
                ),
                {
                    "bearing": 0.9,
                    "heading": 3.01,
                    "remaining_distance": 0.0,
                    "remaining_vertical_distance": 0.0,
                    "estimated_time_of_arrival": "2023-01-01T00:00:00",
                },
            ),
        ],
    )
    def test_navigation_flag_combinations(
        self, characteristic: NavigationCharacteristic, flags: int, data: bytearray, expected: dict[str, Any]
    ) -> None:
        """Test navigation with various flag combinations."""
        result = characteristic.decode_value(data)
        for field, expected_value in expected.items():
            actual_value = getattr(result, field)
            if field == "estimated_time_of_arrival" and expected_value is not None:
                assert actual_value is not None
                # Could check specific date if needed
            else:
                assert actual_value == expected_value, f"Field {field}: expected {expected_value}, got {actual_value}"

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

        result = characteristic.decode_value(data)
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

        result = characteristic.decode_value(data)
        assert result.bearing == 359.99
        assert result.heading == 359.99

    def test_navigation_boundary_values(self, characteristic: NavigationCharacteristic) -> None:
        """Test navigation boundary values."""
        # Test 359.99 degrees (maximum)
        data = bytearray([0x00, 0x00, 0x9F, 0x8C, 0x9F, 0x8C])
        result = characteristic.decode_value(data)
        assert result.bearing == 359.99
        assert result.heading == 359.99

        # Test 0 degrees (minimum)
        data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        result = characteristic.decode_value(data)
        assert result.bearing == 0.0
        assert result.heading == 0.0
