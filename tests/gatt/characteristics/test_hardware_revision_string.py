from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HardwareRevisionStringCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHardwareRevisionStringCharacteristic(CommonCharacteristicTests):
    characteristic_cls = HardwareRevisionStringCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return HardwareRevisionStringCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A27"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"Rev 1.0"), expected_value="Rev 1.0", description="Standard hardware revision"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"HW-A1B2"),
                expected_value="HW-A1B2",
                description="Hardware revision with letters and numbers",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"PCB v2.3"),
                expected_value="PCB v2.3",
                description="PCB version format",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty hardware revision"),
        ]
