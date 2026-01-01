from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import VoltageFrequencyCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoltageFrequencyCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return VoltageFrequencyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2BE8 is Voltage Frequency
        return "2BE8"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),  # 0 Hz
                expected_value=0.0,
                description="Zero frequency",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x32]),  # 50 Hz (50 * 256 = 12800 = 0x3200, but little endian so 0x0032)
                expected_value=50.0,
                description="50 Hz (typical mains frequency)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x3C]),  # 60 Hz (60 * 256 = 15360 = 0x3C00, little endian so 0x003C)
                expected_value=60.0,
                description="60 Hz (typical mains frequency)",
            ),
        ]
