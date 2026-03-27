"""Tests for Device Time characteristic (0x2B90)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics.device_time import (
    DeviceTimeCharacteristic,
    DeviceTimeData,
    DeviceTimeSource,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDeviceTimeCharacteristic(CommonCharacteristicTests):
    """Test suite for Device Time characteristic."""

    @pytest.fixture
    def characteristic(self) -> DeviceTimeCharacteristic:
        return DeviceTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B90"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x07, 0x03, 0x1B, 0x0E, 0x1E, 0x00, 0x01]),
                expected_value=DeviceTimeData(
                    dt=datetime(2024, 3, 27, 14, 30, 0),
                    time_source=DeviceTimeSource.NETWORK_TIME_PROTOCOL,
                ),
                description="2024-03-27 14:30:00 via NTP",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xD2, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00, 0x04]),
                expected_value=DeviceTimeData(
                    dt=datetime(2002, 1, 1, 0, 0, 0),
                    time_source=DeviceTimeSource.MANUAL,
                ),
                description="2002-01-01 00:00:00 manual",
            ),
        ]

    def test_datetime_accessible(self, characteristic: DeviceTimeCharacteristic) -> None:
        """Verify dt field is a standard datetime object."""
        result = characteristic.parse_value(bytearray([0xE8, 0x07, 0x06, 0x0F, 0x0A, 0x1E, 0x3B, 0x02]))
        assert isinstance(result.dt, datetime)
        assert result.dt.year == 2024
        assert result.dt.month == 6
        assert result.dt.hour == 10
        assert result.time_source == DeviceTimeSource.GPS
