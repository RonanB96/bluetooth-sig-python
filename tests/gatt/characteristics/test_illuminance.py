from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import IlluminanceCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIlluminanceCharacteristic(CommonCharacteristicTests):
    characteristic_cls = IlluminanceCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return IlluminanceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AFB"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),  # 0 lux
                expected_value=0.0,
                description="Zero illuminance",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x27, 0x00]),  # 10000 * 0.01 = 100 lux
                expected_value=100.0,
                description="100 lux",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF]),  # 16777215 * 0.01 = 167772.15 lux (max)
                expected_value=167772.15,
                description="Maximum illuminance",
            ),
        ]
