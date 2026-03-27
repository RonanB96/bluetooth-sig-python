"""Tests for DeviceTimeParametersCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.device_time_parameters import (
    DeviceTimeParametersCharacteristic,
    DeviceTimeParametersData,
    TimeProperties,
    TimeUpdateFlags,
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
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=DeviceTimeParametersData(
                    time_update_flags=TimeUpdateFlags(0),
                    time_accuracy=0,
                    time_properties=TimeProperties(0),
                ),
                description="All zeroes - no flags, no accuracy, no properties",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x64, 0x07]),
                expected_value=DeviceTimeParametersData(
                    time_update_flags=TimeUpdateFlags.TIME_UPDATE_PENDING | TimeUpdateFlags.TIME_UPDATE_IN_PROGRESS,
                    time_accuracy=100,
                    time_properties=TimeProperties.TIME_SOURCE_SET
                    | TimeProperties.TIME_ACCURACY_KNOWN
                    | TimeProperties.UTC_ALIGNED,
                ),
                description="Update pending+in progress, accuracy 100, all time properties",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0C, 0x0A, 0x02]),
                expected_value=DeviceTimeParametersData(
                    time_update_flags=TimeUpdateFlags.TIME_ZONE_UPDATE_PENDING | TimeUpdateFlags.DST_UPDATE_PENDING,
                    time_accuracy=10,
                    time_properties=TimeProperties.TIME_ACCURACY_KNOWN,
                ),
                description="Timezone+DST update pending, accuracy 10, accuracy known",
            ),
        ]
