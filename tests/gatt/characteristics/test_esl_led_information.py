"""Tests for ESL LED Information characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_led_information import (
    ESLColorGamut,
    ESLLEDInformationCharacteristic,
    ESLLEDInformationData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestESLLEDInformationCharacteristic(CommonCharacteristicTests):
    """Test suite for ESL LED Information characteristic."""

    @pytest.fixture
    def characteristic(self) -> ESLLEDInformationCharacteristic:
        return ESLLEDInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BFD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01]),
                expected_value=ESLLEDInformationData(
                    led_index=0,
                    color_gamut=ESLColorGamut.RED,
                ),
                description="LED 0, red only",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x07]),
                expected_value=ESLLEDInformationData(
                    led_index=2,
                    color_gamut=ESLColorGamut.RED | ESLColorGamut.GREEN | ESLColorGamut.BLUE,
                ),
                description="LED 2, full RGB gamut",
            ),
        ]
