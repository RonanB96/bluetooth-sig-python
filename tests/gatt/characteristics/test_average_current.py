from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AverageCurrentCharacteristic
from bluetooth_sig.gatt.characteristics.average_current import AverageCurrentData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAverageCurrentCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AverageCurrentCharacteristic:
        return AverageCurrentCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per SIG registry: org.bluetooth.characteristic.average_current = 2AE0
        return "2AE0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        # Format: uint16 current (0.01 A/unit) + uint8 sensing duration (Time Exponential 8)
        # sensing duration raw=0x00 => 0.0 seconds
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=AverageCurrentData(current=0.0, sensing_duration=0.0),
                description="0A, no sensing duration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x27, 0x00]),
                expected_value=AverageCurrentData(current=100.0, sensing_duration=0.0),
                description="100A (typical), no sensing duration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0x00]),
                expected_value=AverageCurrentData(current=655.35, sensing_duration=0.0),
                description="655.35A (max), no sensing duration",
            ),
        ]
