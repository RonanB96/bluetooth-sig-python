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
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),  # 0.00 A, 0.00 A
                expected_value=ElectricCurrentSpecificationData(minimum=0.0, maximum=0.0),
                description="Zero current specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0xC8, 0x00]),  # 1.00 A, 2.00 A
                expected_value=ElectricCurrentSpecificationData(minimum=1.0, maximum=2.0),
                description="Normal current specification (1.0-2.0 A)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF]),  # 655.35 A, 655.35 A
                expected_value=ElectricCurrentSpecificationData(minimum=655.35, maximum=655.35),
                description="Maximum current specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x00, 0x32, 0x00]),  # 0.50 A, 0.50 A
                expected_value=ElectricCurrentSpecificationData(minimum=0.5, maximum=0.5),
                description="Equal min/max current",
            ),
        ]
