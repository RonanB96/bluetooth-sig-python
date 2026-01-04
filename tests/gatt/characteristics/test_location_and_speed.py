"""Tests for Location and Speed characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import LocationAndSpeedCharacteristic
from bluetooth_sig.gatt.characteristics.location_and_speed import (
    ElevationSource,
    HeadingSource,
    LocationAndSpeedData,
    LocationAndSpeedFlags,
    SpeedAndDistanceFormat,
)
from bluetooth_sig.types import PositionStatus
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLocationAndSpeedCharacteristic(CommonCharacteristicTests):
    """Test suite for Location and Speed characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds location and speed-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> LocationAndSpeedCharacteristic:
        """Return a Location and Speed characteristic instance."""
        return LocationAndSpeedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Location and Speed characteristic."""
        return "2A67"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for location and speed."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0xE8, 0x03]),  # flags=0x0001 (speed present), speed=1000 (10.00 m/s)
                expected_value=LocationAndSpeedData(
                    flags=LocationAndSpeedFlags.INSTANTANEOUS_SPEED_PRESENT,
                    instantaneous_speed=10.0,
                    total_distance=None,
                    latitude=None,
                    longitude=None,
                    elevation=None,
                    heading=None,
                    rolling_time=None,
                    utc_time=None,
                    position_status=PositionStatus.NO_POSITION,
                    speed_and_distance_format=SpeedAndDistanceFormat.FORMAT_2D,
                    elevation_source=ElevationSource.POSITIONING_SYSTEM,
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                ),
                description="Location and Speed with instantaneous speed only",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00, 0x90, 0x01, 0x10, 0x27, 0x00]),  # speed + distance
                expected_value=LocationAndSpeedData(
                    flags=LocationAndSpeedFlags.INSTANTANEOUS_SPEED_PRESENT
                    | LocationAndSpeedFlags.TOTAL_DISTANCE_PRESENT,
                    instantaneous_speed=4.0,  # 400 * 0.01 = 4.0 m/s
                    total_distance=1000.0,  # 10000 * 0.1 = 1000.0 m
                    latitude=None,
                    longitude=None,
                    elevation=None,
                    heading=None,
                    rolling_time=None,
                    utc_time=None,
                    position_status=PositionStatus.NO_POSITION,
                    speed_and_distance_format=SpeedAndDistanceFormat.FORMAT_2D,
                    elevation_source=ElevationSource.POSITIONING_SYSTEM,
                    heading_source=HeadingSource.HEADING_BASED_ON_MOVEMENT,
                ),
                description="Location and Speed with speed and distance",
            ),
        ]

    # === Location and Speed-Specific Tests ===
    @pytest.mark.parametrize(
        "flags,data,expected",
        [
            # Minimal: only instantaneous speed
            (
                0x0001,  # INSTANTANEOUS_SPEED_PRESENT
                bytearray([0x01, 0x00, 0xE8, 0x03]),  # speed=1000 (10.00 m/s)
                {
                    "instantaneous_speed": 10.0,
                    "total_distance": None,
                    "latitude": None,
                    "longitude": None,
                    "elevation": None,
                    "heading": None,
                    "rolling_time": None,
                    "utc_time": None,
                },
            ),
            # Speed and distance
            (
                0x0003,  # INSTANTANEOUS_SPEED_PRESENT | TOTAL_DISTANCE_PRESENT
                bytearray([0x03, 0x00, 0xE8, 0x03, 0x00, 0x00, 0x00]),  # speed=1000, distance=0
                {
                    "instantaneous_speed": 10.0,
                    "total_distance": 0.0,
                    "latitude": None,
                    "longitude": None,
                    "elevation": None,
                    "heading": None,
                    "rolling_time": None,
                    "utc_time": None,
                },
            ),
            # Location coordinates
            (
                0x0004,  # LOCATION_PRESENT
                bytearray([0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # lat=0.0, lon=0.0
                {
                    "instantaneous_speed": None,
                    "total_distance": None,
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "elevation": None,
                    "heading": None,
                    "rolling_time": None,
                    "utc_time": None,
                },
            ),
            # Elevation and heading
            (
                0x0018,  # ELEVATION_PRESENT | HEADING_PRESENT
                bytearray([0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # elevation=0.0, heading=0.0
                {
                    "instantaneous_speed": None,
                    "total_distance": None,
                    "latitude": None,
                    "longitude": None,
                    "elevation": 0.0,
                    "heading": 0.0,
                    "rolling_time": None,
                    "utc_time": None,
                },
            ),
            # Rolling time
            (
                0x0020,  # ROLLING_TIME_PRESENT
                bytearray([0x20, 0x00, 0x00]),  # rolling_time=0
                {
                    "instantaneous_speed": None,
                    "total_distance": None,
                    "latitude": None,
                    "longitude": None,
                    "elevation": None,
                    "heading": None,
                    "rolling_time": 0,
                    "utc_time": None,
                },
            ),
            # UTC time
            (
                0x0040,  # UTC_TIME_PRESENT
                bytearray([0x40, 0x00, 0xE7, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00]),  # 2023-01-01 00:00:00
                {
                    "instantaneous_speed": None,
                    "total_distance": None,
                    "latitude": None,
                    "longitude": None,
                    "elevation": None,
                    "heading": None,
                    "rolling_time": None,
                    "utc_time": "2023-01-01T00:00:00",
                },
            ),
        ],
    )
    def test_location_and_speed_flag_combinations(
        self, characteristic: LocationAndSpeedCharacteristic, flags: int, data: bytearray, expected: dict[str, Any]
    ) -> None:
        """Test location and speed with various flag combinations."""
        result = characteristic.parse_value(data)
        for field, expected_value in expected.items():
            actual_value = getattr(result, field)
            if field == "utc_time" and expected_value is not None:
                assert actual_value is not None
                # Could check specific date components if needed
            else:
                assert actual_value == expected_value, f"Field {field}: expected {expected_value}, got {actual_value}"

    def test_location_and_speed_with_all_fields(self, characteristic: LocationAndSpeedCharacteristic) -> None:
        """Test location and speed with all optional fields present."""
        # Flags indicating all fields present + position status OK
        flags = 0xFF | (1 << 8)  # All flags set + position status = POSITION_OK
        data = bytearray(
            [
                flags & 0xFF,
                (flags >> 8) & 0xFF,  # flags (2 bytes)
                0xE8,
                0x03,  # instantaneous_speed (1000 = 10.00 m/s)
                0x00,
                0x00,
                0x00,  # total_distance (0) - 3 bytes
                0x00,
                0x00,
                0x00,
                0x00,  # latitude (0.0)
                0x00,
                0x00,
                0x00,
                0x00,  # longitude (0.0)
                0x00,
                0x00,
                0x00,  # elevation (0.0) - 3 bytes
                0x00,
                0x00,  # heading (0.0 degrees)
                0x00,  # rolling_time (0)
                # UTC time: 2023-01-01 00:00:00
                0xE7,
                0x07,  # year (2023)
                0x01,  # month (1)
                0x01,  # day (1)
                0x00,  # hours (0)
                0x00,  # minutes (0)
                0x00,  # seconds (0)
            ]
        )

        result = characteristic.parse_value(data)
        assert result.instantaneous_speed == 10.0
        assert result.total_distance == 0.0
        assert result.latitude == 0.0
        assert result.longitude == 0.0
        assert result.elevation == 0.0
        assert result.heading == 0.0
        assert result.rolling_time == 0
        assert result.utc_time is not None
        assert result.position_status == PositionStatus.POSITION_OK

    def test_location_and_speed_minimal_data(self, characteristic: LocationAndSpeedCharacteristic) -> None:
        """Test location and speed with minimal data (only flags)."""
        data = bytearray([0x00, 0x00])  # No fields present

        result = characteristic.parse_value(data)
        assert result.instantaneous_speed is None
        assert result.total_distance is None
        assert result.latitude is None
        assert result.longitude is None
        assert result.elevation is None
        assert result.heading is None
        assert result.rolling_time is None
        assert result.utc_time is None
        assert result.position_status == PositionStatus.NO_POSITION
