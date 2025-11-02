from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AverageVoltageCharacteristic

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
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        # Resolution: 1/64 V per unit
        return [
            CharacteristicTestData(input_data=bytearray([0x00, 0x00]), expected_value=0.0, description="0V (min)"),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00]), expected_value=1.0, description="1.0V (64 units)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=1023.984375, description="1023.98V (max)"
            ),
        ]
