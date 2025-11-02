from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import VoltageSpecificationCharacteristic
from bluetooth_sig.gatt.characteristics.voltage_specification import VoltageSpecificationData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoltageSpecificationCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoltageSpecificationCharacteristic:
        return VoltageSpecificationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B19"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),  # 0.00 V, 0.00 V
                expected_value=VoltageSpecificationData(minimum=0.0, maximum=0.0),
                description="Zero voltage specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00, 0x80, 0x00]),  # 1.00 V, 2.00 V (64*1=64, 64*2=128)
                expected_value=VoltageSpecificationData(minimum=1.0, maximum=2.0),
                description="Normal voltage specification (1.0-2.0 V)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF]),  # ~1024 V, ~1024 V
                expected_value=VoltageSpecificationData(minimum=65535 / 64.0, maximum=65535 / 64.0),
                description="Maximum voltage specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x20, 0x00, 0x20, 0x00]),  # 0.50 V, 0.50 V
                expected_value=VoltageSpecificationData(minimum=0.5, maximum=0.5),
                description="Equal min/max voltage",
            ),
        ]
