"""Tests for Ranging Data Ready characteristic (0x2C18)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ranging_data_ready import (
    RangingDataReadyCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRangingDataReadyCharacteristic(CommonCharacteristicTests):
    """Test suite for Ranging Data Ready characteristic."""

    @pytest.fixture
    def characteristic(self) -> RangingDataReadyCharacteristic:
        return RangingDataReadyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C18"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=1,
                description="Ranging counter=1",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1000,
                description="Ranging counter=1000",
            ),
        ]
