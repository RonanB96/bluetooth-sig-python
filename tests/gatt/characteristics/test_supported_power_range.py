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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid supported power range test data.

        FTMS: min(sint16) + max(sint16) + min_increment(uint16) = 6 bytes.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x01, 0x00]),  # Min=0W, Max=0W, Inc=1W
                expected_value=SupportedPowerRangeData(minimum=0, maximum=0, minimum_increment=1),
                description="Zero power range with 1W increment",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0xE8, 0x03, 0x05, 0x00]),  # Min=1W, Max=1000W, Inc=5W
                expected_value=SupportedPowerRangeData(minimum=1, maximum=1000, minimum_increment=5),
                description="1W to 1000W with 5W increment",
            ),
        ]
