from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AverageCurrentCharacteristic

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
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        # 0x2710 = 10000 * 0.01A = 100A
        return [
            CharacteristicTestData(input_data=bytearray([0x00, 0x00]), expected_value=0.0, description="0A (min)"),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x27]), expected_value=100.0, description="100A (typical)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=655.35, description="655.35A (max)"
            ),
        ]
