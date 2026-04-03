"""Tests for DeviceTimeParametersCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.device_time_parameters import (
    DeviceTimeParametersCharacteristic,
    DeviceTimeParametersData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDeviceTimeParametersCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> DeviceTimeParametersCharacteristic:
        return DeviceTimeParametersCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B8F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=DeviceTimeParametersData(
                    rtc_resolution=0,
                ),
                description="RTC resolution unknown (0), no optional fields",
            ),
            CharacteristicTestData(
                # RTC_Resolution=328 (~5ms, as per spec example) [0x48,0x01]
                input_data=bytearray([0x48, 0x01]),
                expected_value=DeviceTimeParametersData(
                    rtc_resolution=328,
                ),
                description="RTC resolution 328/65536 s (~5 ms), no optional fields",
            ),
            CharacteristicTestData(
                # RTC_Resolution=65535 (~1s) [0xFF,0xFF]
                # Max_RTC_Drift_Limit=300s [0x2C,0x01]
                # Max_Days_Until_Sync_Loss=73 days [0x49,0x00]
                # Non_Logged_Time_Adjustment_Limit=10s [0x0A,0x00]
                input_data=bytearray([0xFF, 0xFF, 0x2C, 0x01, 0x49, 0x00, 0x0A, 0x00]),
                expected_value=DeviceTimeParametersData(
                    rtc_resolution=65535,
                    max_rtc_drift_limit=300,
                    max_days_until_sync_loss=73,
                    non_logged_time_adjustment_limit=10,
                ),
                description=(
                    "All RTC drift fields present; 1s resolution, 5-min drift limit,"
                    " 73-day sync loss, 10s non-logged limit"
                ),
            ),
        ]
