from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ElectricCurrentSpecificationCharacteristic
from bluetooth_sig.gatt.characteristics.electric_current_specification import ElectricCurrentSpecificationData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestElectricCurrentSpecificationCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ElectricCurrentSpecificationCharacteristic:
        return ElectricCurrentSpecificationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AF0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid electric current specification test data.

        GSS: 3x uint16 (min, typical, max) at 0.01 A resolution = 6 bytes.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=ElectricCurrentSpecificationData(minimum=0.0, typical=0.0, maximum=0.0),
                description="Zero current specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0x96, 0x00, 0xC8, 0x00]),  # 100=1.0A, 150=1.5A, 200=2.0A
                expected_value=ElectricCurrentSpecificationData(minimum=1.0, typical=1.5, maximum=2.0),
                description="Normal current specification (1.0/1.5/2.0 A)",
            ),
        ]
