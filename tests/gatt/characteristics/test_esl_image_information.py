"""Tests for ESLImageInformationCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_image_information import (
    ESLImageInformationCharacteristic,
    ESLImageInformationData,
    ESLImageType,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestESLImageInformationCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ESLImageInformationCharacteristic:
        return ESLImageInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BFB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x80, 0x00, 0x60, 0x00, 0x00]),
                expected_value=ESLImageInformationData(
                    image_index=0,
                    max_width=128,
                    max_height=96,
                    image_type=ESLImageType.BLACK_WHITE,
                ),
                description="Slot 0, 128x96, black-white",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x40, 0x01, 0xF0, 0x00, 0x07]),
                expected_value=ESLImageInformationData(
                    image_index=3,
                    max_width=320,
                    max_height=240,
                    image_type=ESLImageType.FULL_COLOR,
                ),
                description="Slot 3, 320x240, full colour",
            ),
        ]
