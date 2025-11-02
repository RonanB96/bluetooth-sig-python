from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TxPowerLevelCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTxPowerLevelCharacteristic(CommonCharacteristicTests):
    characteristic_cls = TxPowerLevelCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return TxPowerLevelCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A07"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),  # 0 dBm
                expected_value=0,
                description="Zero power",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]),  # +4 dBm
                expected_value=4,
                description="Positive power",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFC]),  # -4 dBm (252 as signed int8)
                expected_value=-4,
                description="Negative power",
            ),
        ]
