"""Tests for Life Cycle Data characteristic (0x2C0F)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.life_cycle_data import LifeCycleDataCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLifeCycleDataCharacteristic(CommonCharacteristicTests):
    """Test suite for Life Cycle Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> LifeCycleDataCharacteristic:
        return LifeCycleDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C0F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte lifecycle record",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x0B, 0x0C, 0x0D, 0x0E]),
                expected_value=b"\x0a\x0b\x0c\x0d\x0e",
                description="Multi-byte lifecycle record",
            ),
        ]
