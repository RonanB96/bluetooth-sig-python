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
                input_data=bytearray([0x00]),
                expected_value=DeviceTimeFeatureFlags(0),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0F]),
                expected_value=(
                    DeviceTimeFeatureFlags.DEVICE_TIME_SET
                    | DeviceTimeFeatureFlags.TIME_CHANGE_LOGGING
                    | DeviceTimeFeatureFlags.DEVICE_TIME_PERSISTENCE
                    | DeviceTimeFeatureFlags.REFERENCE_TIME_INFORMATION
                ),
                description="All features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=(
                    DeviceTimeFeatureFlags.DEVICE_TIME_SET | DeviceTimeFeatureFlags.DEVICE_TIME_PERSISTENCE
                ),
                description="Device time set and persistence supported",
            ),
        ]
