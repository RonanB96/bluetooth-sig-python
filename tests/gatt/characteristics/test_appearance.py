from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AppearanceCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAppearanceCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AppearanceCharacteristic:
        return AppearanceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A01"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        # Example: Appearance value 0x0040 (64, e.g. "Generic Tag")
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]), expected_value=0, description="Unknown appearance (0x0000)"
            ),
            CharacteristicTestData(input_data=bytearray([0x01, 0x00]), expected_value=1, description="Phone (0x0001)"),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00]), expected_value=64, description="Generic Tag (0x0040)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=65535, description="Max value (0xFFFF)"
            ),
        ]
