"""Tests for AggregateCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.aggregate import AggregateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAggregateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AggregateCharacteristic:
        return AggregateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A5A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b""),
                expected_value=b"",
                description="Empty aggregate passthrough",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03, 0x04]),
                expected_value=b"\x01\x02\x03\x04",
                description="Multi-byte aggregate passthrough",
            ),
        ]
