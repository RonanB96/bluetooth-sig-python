from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ElectricCurrentRangeCharacteristic
from bluetooth_sig.gatt.characteristics.electric_current_range import ElectricCurrentRangeData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestElectricCurrentRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ElectricCurrentRangeCharacteristic:
        return ElectricCurrentRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AEF"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),  # 0.00 A, 0.00 A
                expected_value=ElectricCurrentRangeData(min=0.0, max=0.0),
                description="Zero current range",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0xC8, 0x00]),  # 1.00 A, 2.00 A
                expected_value=ElectricCurrentRangeData(min=1.0, max=2.0),
                description="Normal current range (1.0-2.0 A)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF]),  # 655.35 A, 655.35 A
                expected_value=ElectricCurrentRangeData(min=655.35, max=655.35),
                description="Maximum current range",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x00, 0x32, 0x00]),  # 0.50 A, 0.50 A
                expected_value=ElectricCurrentRangeData(min=0.5, max=0.5),
                description="Equal min/max current",
            ),
        ]
