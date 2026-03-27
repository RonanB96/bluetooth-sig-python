"""Tests for Ranging Data Overwritten characteristic (0x2C19)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ranging_data_overwritten import (
    RangingDataOverwrittenCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRangingDataOverwrittenCharacteristic(CommonCharacteristicTests):
    """Test suite for Ranging Data Overwritten characteristic."""

    @pytest.fixture
    def characteristic(self) -> RangingDataOverwrittenCharacteristic:
        return RangingDataOverwrittenCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C19"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="Ranging counter=0",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]),
                expected_value=65535,
                description="Ranging counter=65535",
            ),
        ]
