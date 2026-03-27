"""Tests for ACSDataOutNotifyCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_data_out_notify import ACSDataOutNotifyCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSDataOutNotifyCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSDataOutNotifyCharacteristic:
        return ACSDataOutNotifyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B31"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xFF]),
                expected_value=b"\xff",
                description="Single byte passthrough",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xAA, 0xBB]),
                expected_value=b"\xaa\xbb",
                description="Two-byte passthrough",
            ),
        ]
