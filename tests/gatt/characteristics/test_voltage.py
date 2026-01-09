from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import VoltageCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoltageCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return VoltageCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2B18 is Voltage
        return "2B18"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        # 1/64 V resolution, so e.g. 3.0 V = 192 (0x00C0)
        return [
            CharacteristicTestData(
                input_data=bytearray([0xC0, 0x00]), expected_value=3.0, description="3.0 V (0x00C0, 1/64 V resolution)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01]), expected_value=4.0, description="4.0 V (0x0100, 1/64 V resolution)"
            ),
        ]
