"""Tests for DeviceTimeFeatureCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.device_time_feature import (
    DeviceTimeFeatureCharacteristic,
    DeviceTimeFeatureFlags,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDeviceTimeFeatureCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> DeviceTimeFeatureCharacteristic:
        return DeviceTimeFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B8E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=DeviceTimeFeatureFlags(0),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00]),
                expected_value=(DeviceTimeFeatureFlags.E2E_CRC | DeviceTimeFeatureFlags.TIME_CHANGE_LOGGING),
                description="E2E-CRC and Time Change Logging features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x1F]),
                expected_value=(
                    DeviceTimeFeatureFlags.E2E_CRC
                    | DeviceTimeFeatureFlags.TIME_CHANGE_LOGGING
                    | DeviceTimeFeatureFlags.BASE_TIME_SECOND_FRACTIONS
                    | DeviceTimeFeatureFlags.TIME_OR_DATE_DISPLAYED_TO_USER
                    | DeviceTimeFeatureFlags.DISPLAYED_FORMATS
                    | DeviceTimeFeatureFlags.DISPLAYED_FORMATS_CHANGEABLE
                    | DeviceTimeFeatureFlags.SEPARATE_USER_TIMELINE
                    | DeviceTimeFeatureFlags.AUTHORIZATION_REQUIRED
                    | DeviceTimeFeatureFlags.RTC_DRIFT_TRACKING
                    | DeviceTimeFeatureFlags.EPOCH_YEAR_1900
                    | DeviceTimeFeatureFlags.EPOCH_YEAR_2000
                    | DeviceTimeFeatureFlags.PROPOSE_NON_LOGGED_TIME_ADJUSTMENT_LIMIT
                    | DeviceTimeFeatureFlags.RETRIEVE_ACTIVE_TIME_ADJUSTMENTS
                ),
                description="All 13 defined features supported (bits 0-12 = 0x1FFF)",
            ),
        ]
