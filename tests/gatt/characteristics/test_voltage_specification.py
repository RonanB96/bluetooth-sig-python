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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid voltage specification test data.

        GSS: 3x uint16 (min, typical, max) at 1/64 V resolution = 6 bytes.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=VoltageSpecificationData(minimum=0.0, typical=0.0, maximum=0.0),
                description="Zero voltage specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00, 0x60, 0x00, 0x80, 0x00]),  # 64/64=1.0, 96/64=1.5, 128/64=2.0
                expected_value=VoltageSpecificationData(minimum=1.0, typical=1.5, maximum=2.0),
                description="Normal voltage specification (1.0/1.5/2.0 V)",
            ),
        ]
