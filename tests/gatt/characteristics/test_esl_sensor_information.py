"""Tests for ESLSensorInformationCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_sensor_information import (
    ESLSensorInformationCharacteristic,
    ESLSensorInformationData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestESLSensorInformationCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ESLSensorInformationCharacteristic:
        return ESLSensorInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BFC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x4E, 0x00]),
                expected_value=ESLSensorInformationData(
                    property_id=0x004E,
                    raw_data=b"",
                ),
                description="Property ID only, no payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0xAB, 0xCD]),
                expected_value=ESLSensorInformationData(
                    property_id=0x0001,
                    raw_data=b"\xab\xcd",
                ),
                description="Property ID with 2-byte payload",
            ),
        ]
