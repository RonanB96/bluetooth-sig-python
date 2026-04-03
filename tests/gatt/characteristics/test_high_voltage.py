from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import HighVoltageCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHighVoltageCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return HighVoltageCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2BE0 is High Voltage
        return "2BE0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid high voltage test data.

        GSS: uint24, resolution 1/64 V.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=0.0,
                description="Zero voltage",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00, 0x00]),  # 64 * (1/64) = 1.0 V
                expected_value=1.0,
                description="1 volt (raw=64)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x27, 0x00]),  # 10000 * (1/64) = 156.25 V
                expected_value=156.25,
                description="156.25 volts (raw=10000)",
            ),
        ]
