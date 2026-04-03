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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid electric current statistics test data.

        GSS: avg(uint16) + std_dev(uint16) + min(uint16) + max(uint16) + sensing_dur(uint8)
        = 9 bytes. All current fields at 0.01 A resolution.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=ElectricCurrentStatisticsData(
                    average=0.0, standard_deviation=0.0, minimum=0.0, maximum=0.0, sensing_duration=0.0
                ),
                description="Zero current statistics",
            ),
            CharacteristicTestData(
                # avg=150(1.5A), std=10(0.1A), min=100(1.0A), max=200(2.0A), dur=64(1.0s)
                input_data=bytearray([0x96, 0x00, 0x0A, 0x00, 0x64, 0x00, 0xC8, 0x00, 0x40]),
                expected_value=ElectricCurrentStatisticsData(
                    average=1.5, standard_deviation=0.1, minimum=1.0, maximum=2.0, sensing_duration=1.0
                ),
                description="Normal current statistics",
            ),
        ]
