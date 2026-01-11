from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import VoltageStatisticsCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.voltage_statistics import VoltageStatisticsData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoltageStatisticsCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return VoltageStatisticsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B1A"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # All zeros
                expected_value=VoltageStatisticsData(minimum=0.0, maximum=0.0, average=0.0),
                description="Zero voltage statistics",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x0C, 0x00, 0x0F, 0x40, 0x0D]),  # 3200, 3840, 3392 -> 50V, 60V, 53V
                expected_value=VoltageStatisticsData(minimum=50.0, maximum=60.0, average=53.0),
                description="Typical voltage range (50V-60V)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),  # Max values
                expected_value=VoltageStatisticsData(minimum=1023.984375, maximum=1023.984375, average=1023.984375),
                description="Maximum voltage values",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x02, 0x00, 0x01, 0x00]),  # 1, 2, 1 -> 0.015625V, 0.03125V, 0.015625V
                expected_value=VoltageStatisticsData(minimum=0.015625, maximum=0.03125, average=0.015625),
                description="Low voltage values with precision",
            ),
        ]
