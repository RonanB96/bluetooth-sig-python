"""Tests for Work Cycle Data characteristic (0x2C10)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.work_cycle_data import WorkCycleDataCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestWorkCycleDataCharacteristic(CommonCharacteristicTests):
    """Test suite for Work Cycle Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> WorkCycleDataCharacteristic:
        return WorkCycleDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C10"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xFF]),
                expected_value=b"\xff",
                description="Single byte work cycle record",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03, 0x04]),
                expected_value=b"\x01\x02\x03\x04",
                description="Multi-byte work cycle record",
            ),
        ]
