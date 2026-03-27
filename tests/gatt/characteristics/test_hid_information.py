"""Tests for HidInformationCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.hid_information import (
    HidInformationCharacteristic,
    HidInformationData,
    HidInformationFlags,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestHidInformationCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> HidInformationCharacteristic:
        return HidInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A4A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x11, 0x01, 0x00, 0x01]),
                expected_value=HidInformationData(
                    bcd_hid=0x0111,
                    b_country_code=0,
                    flags=HidInformationFlags.REMOTE_WAKE,
                ),
                description="HID v1.11, no country, remote wake",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x02, 0x21, 0x03]),
                expected_value=HidInformationData(
                    bcd_hid=0x0200,
                    b_country_code=0x21,
                    flags=HidInformationFlags.REMOTE_WAKE | HidInformationFlags.NORMALLY_CONNECTABLE,
                ),
                description="HID v2.0, US country code, both flags",
            ),
        ]
