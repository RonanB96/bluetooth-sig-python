"""Tests for ACSDataOutIndicateCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_data_out_indicate import ACSDataOutIndicateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSDataOutIndicateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSDataOutIndicateCharacteristic:
        return ACSDataOutIndicateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B32"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x42]),
                expected_value=b"\x42",
                description="Single byte passthrough",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03]),
                expected_value=b"\x01\x02\x03",
                description="Multi-byte passthrough",
            ),
        ]
