"""Tests for ObjectSizeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.object_size import (
    ObjectSizeCharacteristic,
    ObjectSizeData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestObjectSizeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ObjectSizeCharacteristic:
        return ObjectSizeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x04, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00]),
                expected_value=ObjectSizeData(
                    current_size=1024,
                    allocated_size=2048,
                ),
                description="current=1024, allocated=2048",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00]),
                expected_value=ObjectSizeData(
                    current_size=0,
                    allocated_size=4096,
                ),
                description="current=0, allocated=4096",
            ),
        ]
