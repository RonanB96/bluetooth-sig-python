from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import NoiseCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestNoiseCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return NoiseCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2BE4 is Noise
        return "2BE4"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),  # 0 dB
                expected_value=0,
                description="Zero noise level",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32]),  # 50 dB (typical conversation level)
                expected_value=50,
                description="50 dB (conversation level)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFD]),  # 253 dB (max normal value)
                expected_value=253,
                description="253 dB (maximum normal value)",
            ),
        ]
