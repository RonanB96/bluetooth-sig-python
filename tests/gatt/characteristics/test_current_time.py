"""Tests for Current Time characteristic (0x2A2B)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics.current_time import CurrentTimeCharacteristic
from bluetooth_sig.gatt.characteristics.templates import TimeData
from bluetooth_sig.types.gatt_enums import AdjustReason, DayOfWeek
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCurrentTimeCharacteristic(CommonCharacteristicTests):
    """Test suite for Current Time characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds current time-specific validation and edge cases.
    """

    @pytest.fixture
    def characteristic(self) -> CurrentTimeCharacteristic:
        """Return a Current Time characteristic instance."""
        return CurrentTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Current Time characteristic."""
        return "2A2B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for current time (2025-01-15 14:30:45.128 Wednesday)."""
        # 2025-01-15 14:30:45.128 Wednesday, manual time update
        data = bytearray(
            [
                0xE9,
                0x07,  # Year: 2025 (little-endian)
                0x01,  # Month: January
                0x0F,  # Day: 15
                0x0E,  # Hours: 14
                0x1E,  # Minutes: 30
                0x2D,  # Seconds: 45
                0x03,  # Day of Week: Wednesday
                0x21,  # Fractions256: 33 (~0.128 seconds)
                0x01,  # Adjust Reason: Manual time update
            ]
        )
        expected = TimeData(
            date_time=datetime(2025, 1, 15, 14, 30, 45),
            day_of_week=DayOfWeek.WEDNESDAY,
            fractions256=33,
            adjust_reason=AdjustReason.MANUAL_TIME_UPDATE,
        )

        # Midnight on Monday with no adjustments
        data_midnight = bytearray([0xE9, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00])
        expected_midnight = TimeData(
            date_time=datetime(2025, 1, 1, 0, 0, 0),
            day_of_week=DayOfWeek.MONDAY,
            fractions256=0,
            adjust_reason=AdjustReason.from_raw(0),
        )

        # End of day with multiple adjust reasons (external ref + timezone change)
        data_eod = bytearray([0xE9, 0x07, 0x0C, 0x1F, 0x17, 0x3B, 0x3B, 0x07, 0xFF, 0x06])
        expected_eod = TimeData(
            date_time=datetime(2025, 12, 31, 23, 59, 59),
            day_of_week=DayOfWeek.SUNDAY,
            fractions256=255,
            adjust_reason=AdjustReason.EXTERNAL_REFERENCE_TIME_UPDATE | AdjustReason.CHANGE_OF_TIME_ZONE,
        )

        return [
            CharacteristicTestData(
                input_data=data, expected_value=expected, description="2025-01-15 14:30:45.128 Wednesday"
            ),
            CharacteristicTestData(
                input_data=data_midnight, expected_value=expected_midnight, description="2025-01-01 00:00:00 Monday"
            ),
            CharacteristicTestData(
                input_data=data_eod,
                expected_value=expected_eod,
                description="2025-12-31 23:59:59.996 Sunday with adjust reasons",
            ),
        ]

    # === Current Time-Specific Tests ===
    def test_current_time_with_unknown_fields(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test current time with unknown year, month, and day."""
        # Unknown date (0000-00-00) but valid time and day of week
        data = bytearray(
            [
                0x00,
                0x00,  # Year: 0 (unknown)
                0x00,  # Month: 0 (unknown)
                0x00,  # Day: 0 (unknown)
                0x0C,  # Hours: 12
                0x1E,  # Minutes: 30
                0x00,  # Seconds: 0
                0x01,  # Day of Week: Monday
                0x00,  # Fractions256: 0
                0x00,  # Adjust Reason: none
            ]
        )
        result = characteristic.parse_value(data)
        assert result.value is not None
        assert result.value.date_time is None  # Unknown date
        assert result.value.day_of_week == DayOfWeek.MONDAY

    def test_current_time_boundary_year(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test current time with boundary year values."""
        # Minimum valid year (1582)
        data_min = bytearray([0x2E, 0x06, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00])
        result_min = characteristic.parse_value(data_min)
        assert result_min.value is not None
        assert result_min.value.date_time is not None
        assert result_min.value.date_time.year == 1582

        # Maximum valid year (9999)
        data_max = bytearray([0x0F, 0x27, 0x0C, 0x1F, 0x17, 0x3B, 0x3B, 0x07, 0xFF, 0x0F])
        result_max = characteristic.parse_value(data_max)
        assert result_max.value is not None
        assert result_max.value.date_time is not None
        assert result_max.value.date_time.year == 9999

    def test_current_time_invalid_year(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that invalid years are rejected."""
        # Year too low (1) - datetime.MINYEAR is 1, but year 1 is technically valid
        # We test year 10000 which exceeds datetime.MAXYEAR (9999)
        data_high = bytearray([0x10, 0x27, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00])
        result = characteristic.parse_value(data_high)
        assert not result.parse_success
        assert "year" in result.error_message.lower() or "out of range" in result.error_message.lower()

    def test_current_time_invalid_month(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that invalid months are rejected."""
        data = bytearray([0xE9, 0x07, 0x0D, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00])  # Month: 13
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "month" in result.error_message.lower()

    def test_current_time_invalid_day(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that invalid days are rejected."""
        data = bytearray([0xE9, 0x07, 0x01, 0x20, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00])  # Day: 32
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "day" in result.error_message.lower()

    def test_current_time_invalid_hours(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that invalid hours are rejected."""
        data = bytearray([0xE9, 0x07, 0x01, 0x01, 0x18, 0x00, 0x00, 0x01, 0x00, 0x00])  # Hours: 24
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "hour" in result.error_message.lower()  # Python datetime says "hour"

    def test_current_time_invalid_minutes(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that invalid minutes are rejected."""
        data = bytearray([0xE9, 0x07, 0x01, 0x01, 0x00, 0x3C, 0x00, 0x01, 0x00, 0x00])  # Minutes: 60
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "minute" in result.error_message.lower()  # Python datetime says "minute"

    def test_current_time_invalid_seconds(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that invalid seconds are rejected."""
        data = bytearray([0xE9, 0x07, 0x01, 0x01, 0x00, 0x00, 0x3C, 0x01, 0x00, 0x00])  # Seconds: 60
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "second" in result.error_message.lower()  # Python datetime says "second"

    def test_current_time_invalid_day_of_week(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that invalid day of week values are rejected."""
        data = bytearray([0xE9, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00])  # Day of Week: 8
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "day_of_week" in result.error_message.lower()

    @pytest.mark.parametrize(
        "day_of_week,expected_enum",
        [
            (0, DayOfWeek.UNKNOWN),
            (1, DayOfWeek.MONDAY),
            (2, DayOfWeek.TUESDAY),
            (3, DayOfWeek.WEDNESDAY),
            (4, DayOfWeek.THURSDAY),
            (5, DayOfWeek.FRIDAY),
            (6, DayOfWeek.SATURDAY),
            (7, DayOfWeek.SUNDAY),
        ],
    )
    def test_current_time_day_of_week_values(
        self, characteristic: CurrentTimeCharacteristic, day_of_week: int, expected_enum: DayOfWeek
    ) -> None:
        """Test all valid day of week values."""
        data = bytearray([0xE9, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00, day_of_week, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert result.value is not None
        assert result.value.day_of_week == expected_enum

    def test_current_time_adjust_reason_flags(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test adjust reason bitfield values."""
        # Manual time update
        data_manual = bytearray([0xE9, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01])
        result = characteristic.parse_value(data_manual)
        assert result.value is not None
        assert result.value.adjust_reason & AdjustReason.MANUAL_TIME_UPDATE

        # Multiple reasons
        data_multi = bytearray([0xE9, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x0F])
        result = characteristic.parse_value(data_multi)
        assert result.value is not None
        assert result.value.adjust_reason & AdjustReason.MANUAL_TIME_UPDATE
        assert result.value.adjust_reason & AdjustReason.EXTERNAL_REFERENCE_TIME_UPDATE
        assert result.value.adjust_reason & AdjustReason.CHANGE_OF_TIME_ZONE
        assert result.value.adjust_reason & AdjustReason.CHANGE_OF_DST

    def test_current_time_roundtrip(self, characteristic: CurrentTimeCharacteristic) -> None:
        """Test that encode/decode are inverse operations."""
        original = TimeData(
            date_time=datetime(2025, 11, 1, 14, 30, 45),
            day_of_week=DayOfWeek.SATURDAY,
            fractions256=128,
            adjust_reason=AdjustReason.EXTERNAL_REFERENCE_TIME_UPDATE,
        )

        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded.value is not None

        assert decoded.value.date_time == original.date_time
        assert decoded.value.day_of_week == original.day_of_week
        assert decoded.value.fractions256 == original.fractions256
        assert decoded.value.adjust_reason == original.adjust_reason
