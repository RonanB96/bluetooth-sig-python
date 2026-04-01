"""Tests for Time with DST characteristic (0x2A11)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics.dst_offset import DSTOffset
from bluetooth_sig.gatt.characteristics.time_with_dst import TimeWithDstCharacteristic, TimeWithDstData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTimeWithDstCharacteristic(CommonCharacteristicTests):
    """Test suite for Time with DST characteristic."""

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
        # 2020-01-01 00:00:00, DST=STANDARD_TIME
        data1 = bytearray([0xE4, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00])
        expected1 = TimeWithDstData(
            dt=datetime(2020, 1, 1, 0, 0, 0),
            dst_offset=DSTOffset.STANDARD_TIME,
        )

        # 2022-06-15 12:30:00, DST=DAYLIGHT_TIME
        data2 = bytearray([0xE6, 0x07, 0x06, 0x0F, 0x0C, 0x1E, 0x00, 0x04])
        expected2 = TimeWithDstData(
            dt=datetime(2022, 6, 15, 12, 30, 0),
            dst_offset=DSTOffset.DAYLIGHT_TIME,
        )

        return [
            CharacteristicTestData(
                input_data=data1,
                expected_value=expected1,
                description="2020-01-01 00:00:00 Standard Time",
            ),
            CharacteristicTestData(
                input_data=data2,
                expected_value=expected2,
                description="2022-06-15 12:30:00 Daylight Time",
            ),
        ]

    def test_roundtrip(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test encode/decode roundtrip consistency."""
        original = TimeWithDstData(
            dt=datetime(2024, 3, 10, 2, 0, 0),
            dst_offset=DSTOffset.DAYLIGHT_TIME,
        )
        encoded = characteristic.build_value(original)
        result = characteristic.parse_value(encoded)
        assert result == original

    def test_half_hour_daylight(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test half-hour daylight DST offset."""
        data = bytearray([0xE8, 0x07, 0x09, 0x1E, 0x02, 0x00, 0x00, 0x02])
        result = characteristic.parse_value(data)
        assert result.dst_offset == DSTOffset.HALF_HOUR_DAYLIGHT
        assert result.dt == datetime(2024, 9, 30, 2, 0, 0)

    def test_double_daylight(self, characteristic: TimeWithDstCharacteristic) -> None:
        """Test double daylight DST offset."""
        data = bytearray([0xE8, 0x07, 0x06, 0x01, 0x0C, 0x00, 0x00, 0x08])
        result = characteristic.parse_value(data)
        assert result.dst_offset == DSTOffset.DOUBLE_DAYLIGHT
