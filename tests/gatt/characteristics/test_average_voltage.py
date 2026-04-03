from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AverageVoltageCharacteristic
from bluetooth_sig.gatt.characteristics.average_voltage import AverageVoltageData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAverageVoltageCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AverageVoltageCharacteristic:
        return AverageVoltageCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per SIG registry: org.bluetooth.characteristic.average_voltage = 2AE1
        return "2AE1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        # Format: uint16 voltage (1/64 V/unit) + uint8 sensing duration (Time Exponential 8)
        # sensing duration raw=0x00 => 0.0 seconds
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=AverageVoltageData(voltage=0.0, sensing_duration=0.0),
                description="0V, no sensing duration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00, 0x00]),
                expected_value=AverageVoltageData(voltage=1.0, sensing_duration=0.0),
                description="1.0V (64 units), no sensing duration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0x00]),
                expected_value=AverageVoltageData(voltage=1023.984375, sensing_duration=0.0),
                description="1023.98V (max), no sensing duration",
            ),
        ]
