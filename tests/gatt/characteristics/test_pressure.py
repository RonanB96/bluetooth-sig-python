from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PressureCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPressureCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return PressureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A6D"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=0.0,
                description="0 Pa (minimum pressure)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x76, 0x0F, 0x00]),
                expected_value=101325.0,
                description="101325 Pa (standard atmospheric pressure)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x84, 0x1E, 0x00]),
                expected_value=200000.0,
                description="200000 Pa (maximum pressure)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x27, 0x00, 0x00]), expected_value=1000.0, description="1000 Pa (1 kPa)"
            ),
        ]
