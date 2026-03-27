"""Tests for ESLDisplayInformationCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_display_information import (
    ESLDisplayInformationCharacteristic,
    ESLDisplayInformationData,
    ESLDisplayType,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestESLDisplayInformationCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ESLDisplayInformationCharacteristic:
        return ESLDisplayInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BFA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # display_index=0, width=128 (0x0080 LE), height=64 (0x0040 LE), display_type=BLACK_WHITE
                input_data=bytearray([0x00, 0x80, 0x00, 0x40, 0x00, 0x01]),
                expected_value=ESLDisplayInformationData(
                    display_index=0,
                    width=128,
                    height=64,
                    display_type=ESLDisplayType.BLACK_WHITE,
                ),
                description="Display 0: 128x64 black and white",
            ),
            CharacteristicTestData(
                # display_index=2, width=320 (0x0140 LE), height=240 (0x00F0 LE), display_type=COLOR_RGB
                input_data=bytearray([0x02, 0x40, 0x01, 0xF0, 0x00, 0x06]),
                expected_value=ESLDisplayInformationData(
                    display_index=2,
                    width=320,
                    height=240,
                    display_type=ESLDisplayType.COLOR_RGB,
                ),
                description="Display 2: 320x240 colour RGB",
            ),
            CharacteristicTestData(
                # display_index=1, width=200 (0x00C8 LE), height=200 (0x00C8 LE), display_type=FOUR_GRAY
                input_data=bytearray([0x01, 0xC8, 0x00, 0xC8, 0x00, 0x03]),
                expected_value=ESLDisplayInformationData(
                    display_index=1,
                    width=200,
                    height=200,
                    display_type=ESLDisplayType.FOUR_GRAY,
                ),
                description="Display 1: 200x200 four grey scale",
            ),
        ]
