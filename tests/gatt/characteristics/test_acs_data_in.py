"""Tests for ACSDataInCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_data_in import ACSDataInCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSDataInCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSDataInCharacteristic:
        return ACSDataInCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B30"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte passthrough",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xDE, 0xAD, 0xBE, 0xEF]),
                expected_value=b"\xde\xad\xbe\xef",
                description="Multi-byte passthrough",
            ),
        ]
