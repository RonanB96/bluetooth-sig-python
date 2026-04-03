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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid voltage statistics test data.

        GSS: avg(uint16) + std_dev(uint16) + min(uint16) + max(uint16) + sensing_dur(uint8)
        = 9 bytes. All voltage fields at 1/64 V resolution.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=VoltageStatisticsData(
                    average=0.0, standard_deviation=0.0, minimum=0.0, maximum=0.0, sensing_duration=0.0
                ),
                description="Zero voltage statistics",
            ),
            CharacteristicTestData(
                # avg=3392(53V), std=64(1V), min=3200(50V), max=3840(60V), dur=64(1.0s)
                input_data=bytearray([0x40, 0x0D, 0x40, 0x00, 0x80, 0x0C, 0x00, 0x0F, 0x40]),
                expected_value=VoltageStatisticsData(
                    average=53.0, standard_deviation=1.0, minimum=50.0, maximum=60.0, sensing_duration=1.0
                ),
                description="Typical voltage statistics",
            ),
        ]
