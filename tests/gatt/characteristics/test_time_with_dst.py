"""Tests for Time with DST characteristic (0x2A11)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics.templates import TimeData
from bluetooth_sig.gatt.characteristics.time_with_dst import (
    TimeWithDstCharacteristic,
)
from bluetooth_sig.types.gatt_enums import AdjustReason, DayOfWeek
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTimeWithDstCharacteristic(CommonCharacteristicTests):
    """Test suite for Time with DST characteristic.

    Inherits behavioral tests from CommonCharacteristicTests.
    Adds time with DST-specific validation and edge cases.
    """

    @pytest.fixture
    def characteristic(self) -> TimeWithDstCharacteristic:
        """Return a Time with DST characteristic instance."""
        return TimeWithDstCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Time with DST characteristic."""
        return "2A11"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for time with DST."""
        # March 10, 2024 02:00:00 Sunday (DST change in US)
        data = bytearray(
            [
                0xE8,
                0x07,  # Year: 2024 (little-endian)
                0x03,  # Month: March
                0x0A,  # Day: 10
                0x02,  # Hours: 2
                0x00,  # Minutes: 0
                0x00,  # Seconds: 0
                0x07,  # Day of Week: Sunday
                0x00,  # Fractions256: 0
                0x08,  # Adjust Reason: DST change
            ]
        )
        expected = TimeData(
            date_time=datetime(2024, 3, 10, 2, 0, 0),
            day_of_week=DayOfWeek.SUNDAY,
            fractions256=0,
            adjust_reason=AdjustReason.CHANGE_OF_DST,  # DST change
        )

        # November 3, 2024 02:00:00 Sunday (DST change in US)
        data_fall = bytearray([0xE8, 0x07, 0x0B, 0x03, 0x02, 0x00, 0x00, 0x07, 0x80, 0x08])
        expected_fall = TimeData(
            date_time=datetime(2024, 11, 3, 2, 0, 0),
            day_of_week=DayOfWeek.SUNDAY,
            fractions256=128,  # ~0.5 seconds
            adjust_reason=AdjustReason.CHANGE_OF_DST,  # DST change
        )

        # Unknown date/time (all zeros for date)
        data_unknown = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        expected_unknown = TimeData(
            date_time=None,
            day_of_week=DayOfWeek.UNKNOWN,
            fractions256=0,
            adjust_reason=AdjustReason.from_raw(0),
        )

        return [
            CharacteristicTestData(
                input_data=data, expected_value=expected, description="2024-03-10 02:00:00 Sunday DST change"
            ),
            CharacteristicTestData(
                input_data=data_fall, expected_value=expected_fall, description="2024-11-03 02:00:00 Sunday DST change"
            ),
            CharacteristicTestData(
                input_data=data_unknown, expected_value=expected_unknown, description="Unknown date/time"
            ),
        ]

    # === Time with DST-Specific Tests ===
    def test_time_with_dst_boundary_values(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test boundary values for time with DST fields."""
        # Maximum fractions256 (255)
        data_max_fractions = bytearray([0xE8, 0x07, 0x03, 0x0A, 0x02, 0x00, 0x00, 0x07, 0xFF, 0x08])
        result_fractions = characteristic.parse_value(data_max_fractions)
        assert result_fractions.parse_success
        assert result_fractions.value is not None
        assert result_fractions.value.fractions256 == 255

        # Maximum adjust reason (255, but reserved bits are masked to 15)
        data_max_adjust = bytearray([0xE8, 0x07, 0x03, 0x0A, 0x02, 0x00, 0x00, 0x07, 0x00, 0xFF])
        result_adjust = characteristic.parse_value(data_max_adjust)
        assert result_adjust.parse_success
        assert result_adjust.value is not None
        # Reserved bits (4-7) are masked out, so 255 becomes 15 (all defined flags)
        assert result_adjust.value.adjust_reason == AdjustReason(15)

    def test_time_with_dst_invalid_day_of_week(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test that invalid day of week values are rejected."""
        # Day of week = 8 (invalid, max is 7)
        data = bytearray([0xE8, 0x07, 0x03, 0x0A, 0x02, 0x00, 0x00, 0x08, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "day_of_week" in result.error_message.lower()

    def test_time_with_dst_invalid_fractions256(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test that invalid fractions256 values are rejected during encoding."""
        from bluetooth_sig.gatt.exceptions import ValueRangeError

        data = TimeData(
            date_time=datetime(2024, 3, 10, 2, 0, 0),
            day_of_week=DayOfWeek.SUNDAY,
            fractions256=256,  # Invalid (max is 255)
            adjust_reason=AdjustReason.from_raw(0),
        )
        with pytest.raises(ValueRangeError, match="fractions256"):
            characteristic.encode_value(data)

    def test_time_with_dst_invalid_adjust_reason(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test that invalid adjust reason values are rejected during encoding."""
        from bluetooth_sig.gatt.exceptions import ValueRangeError

        data = TimeData(
            date_time=datetime(2024, 3, 10, 2, 0, 0),
            day_of_week=DayOfWeek.SUNDAY,
            fractions256=0,
            adjust_reason=AdjustReason(256),  # Invalid (max is 255)
        )
        with pytest.raises(ValueRangeError, match="adjust_reason"):
            characteristic.encode_value(data)

    def test_time_with_dst_roundtrip(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test encode/decode roundtrip consistency."""
        original = TimeData(
            date_time=datetime(2024, 3, 10, 2, 0, 0),
            day_of_week=DayOfWeek.SUNDAY,
            fractions256=128,
            adjust_reason=AdjustReason.CHANGE_OF_DST,
        )

        encoded = characteristic.encode_value(original)
        result = characteristic.parse_value(encoded)

        assert result.parse_success
        assert result.value is not None
        assert result.value == original
