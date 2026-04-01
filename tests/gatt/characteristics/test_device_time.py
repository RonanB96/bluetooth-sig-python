"""Tests for Device Time characteristic (0x2B90)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.device_time import (
    DeviceTimeCharacteristic,
    DeviceTimeData,
    DTStatus,
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
                # Base_Time=0 [0x00,0x00,0x00,0x00], Time_Zone=0 [0x00],
                # DST_Offset=0 [0x00], DT_Status=0 [0x00,0x00]
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=DeviceTimeData(
                    base_time=0,
                    time_zone=0,
                    dst_offset=0,
                    dt_status=DTStatus(0),
                ),
                description="All zeros - epoch start, UTC+0, no DST, no status flags",
            ),
            CharacteristicTestData(
                # Base_Time=86400 (1 day) [0x80,0x51,0x01,0x00], Time_Zone=8 (UTC+2h) [0x08],
                # DST_Offset=4 (+1h) [0x04], DT_Status=UTC_ALIGNED [0x02,0x00]
                input_data=bytearray([0x80, 0x51, 0x01, 0x00, 0x08, 0x04, 0x02, 0x00]),
                expected_value=DeviceTimeData(
                    base_time=86400,
                    time_zone=8,
                    dst_offset=4,
                    dt_status=DTStatus.UTC_ALIGNED,
                ),
                description="1 day since epoch, UTC+2h, DST+1h, UTC aligned",
            ),
            CharacteristicTestData(
                # Base_Time=670791488 [0x40,0x77,0xFB,0x27], Time_Zone=-20 (UTC-5h) [0xEC],
                # DST_Offset=255 (unknown) [0xFF],
                # DT_Status=TIME_FAULT|EPOCH_YEAR_2000 [0x11,0x00]
                input_data=bytearray([0x40, 0x77, 0xFB, 0x27, 0xEC, 0xFF, 0x11, 0x00]),
                expected_value=DeviceTimeData(
                    base_time=670791488,
                    time_zone=-20,
                    dst_offset=255,
                    dt_status=DTStatus.TIME_FAULT | DTStatus.EPOCH_YEAR_2000,
                ),
                description="Large base_time, UTC-5h, unknown DST, time fault with epoch 2000",
            ),
        ]
