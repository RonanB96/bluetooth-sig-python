from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ElectricCurrentCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestElectricCurrentCharacteristic(CommonCharacteristicTests):
    characteristic_cls = ElectricCurrentCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return ElectricCurrentCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AEE"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),  # 0 A
                expected_value=0.0,
                description="Zero current",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x96, 0x00]),  # 150 * 0.01 = 1.5 A
                expected_value=1.5,
                description="1.5 amperes",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]),  # 65535 * 0.01 = 655.35 A (max)
                expected_value=655.35,
                description="Maximum current",
            ),
        ]
