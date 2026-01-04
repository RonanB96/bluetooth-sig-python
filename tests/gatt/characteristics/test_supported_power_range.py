from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import SupportedPowerRangeCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.supported_power_range import SupportedPowerRangeData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSupportedPowerRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return SupportedPowerRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2AD8 is Supported Power Range
        return "2AD8"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),  # Min=0W, Max=0W
                expected_value=SupportedPowerRangeData(minimum=0, maximum=0),
                description="Zero power range",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0xE8, 0x03]),  # Min=1W, Max=1000W (0x03E8 = 1000)
                expected_value=SupportedPowerRangeData(minimum=1, maximum=1000),
                description="1W to 1000W power range",
            ),
        ]
