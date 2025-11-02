from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FirmwareRevisionStringCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFirmwareRevisionStringCharacteristic(CommonCharacteristicTests):
    characteristic_cls = FirmwareRevisionStringCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return FirmwareRevisionStringCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A26"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"1.2.3"), expected_value="1.2.3", description="Standard version format"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"v2.1.0-beta"),
                expected_value="v2.1.0-beta",
                description="Version with beta suffix",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"2023.07.15"),
                expected_value="2023.07.15",
                description="Date-based version",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty firmware version"),
        ]
