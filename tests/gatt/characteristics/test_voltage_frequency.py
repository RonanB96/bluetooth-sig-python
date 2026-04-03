from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import VoltageFrequencyCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoltageFrequencyCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return VoltageFrequencyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2BE8 is Voltage Frequency
        return "2BE8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid voltage frequency test data.

        GSS: uint16, M=1 d=0 b=0 (resolution 1 Hz).
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="Zero frequency",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x00]),  # 50 LE
                expected_value=50,
                description="50 Hz (typical mains frequency)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x3C, 0x00]),  # 60 LE
                expected_value=60,
                description="60 Hz (typical mains frequency)",
            ),
        ]
