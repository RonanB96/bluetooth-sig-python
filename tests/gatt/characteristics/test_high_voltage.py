from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HighVoltageCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHighVoltageCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return HighVoltageCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2BE0 is High Voltage
        return "2BE0"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),  # 0 V
                expected_value=0.0,
                description="Zero voltage",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),  # 1 V
                expected_value=1.0,
                description="1 volt",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF]),  # 16777215 V (max uint24)
                expected_value=16777215.0,
                description="Maximum voltage",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x27, 0x00]),  # 10000 V
                expected_value=10000.0,
                description="10,000 volts",
            ),
        ]
