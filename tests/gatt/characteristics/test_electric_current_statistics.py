from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ElectricCurrentStatisticsCharacteristic
from bluetooth_sig.gatt.characteristics.electric_current_statistics import ElectricCurrentStatisticsData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestElectricCurrentStatisticsCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ElectricCurrentStatisticsCharacteristic:
        return ElectricCurrentStatisticsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AF1"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # 0.00 A, 0.00 A, 0.00 A
                expected_value=ElectricCurrentStatisticsData(minimum=0.0, maximum=0.0, average=0.0),
                description="Zero current statistics",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0xC8, 0x00, 0x96, 0x00]),  # 1.00 A, 2.00 A, 1.50 A
                expected_value=ElectricCurrentStatisticsData(minimum=1.0, maximum=2.0, average=1.5),
                description="Normal current statistics (1.0-2.0 A, avg 1.5 A)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),  # 655.35 A, 655.35 A, 655.35 A
                expected_value=ElectricCurrentStatisticsData(minimum=655.35, maximum=655.35, average=655.35),
                description="Maximum current statistics",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x00, 0x64, 0x00, 0x4B, 0x00]),  # 0.50 A, 1.00 A, 0.75 A
                expected_value=ElectricCurrentStatisticsData(minimum=0.5, maximum=1.0, average=0.75),
                description="Current statistics with different values",
            ),
        ]
