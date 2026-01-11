from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import SoftwareRevisionStringCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSoftwareRevisionStringCharacteristic(CommonCharacteristicTests):
    characteristic_cls = SoftwareRevisionStringCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return SoftwareRevisionStringCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A28"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"3.1.4"), expected_value="3.1.4", description="Standard software version"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"v1.0.0-alpha"),
                expected_value="v1.0.0-alpha",
                description="Version with alpha suffix",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"2.0.1-hotfix"),
                expected_value="2.0.1-hotfix",
                description="Version with hotfix suffix",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty software version"),
        ]
