"""Tests for Active Preset Index characteristic (0x2BDC)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.active_preset_index import ActivePresetIndexCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestActivePresetIndexCharacteristic(CommonCharacteristicTests):
    """Test suite for Active Preset Index characteristic."""

    @pytest.fixture
    def characteristic(self) -> ActivePresetIndexCharacteristic:
        return ActivePresetIndexCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BDC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Index 0"),
            CharacteristicTestData(bytearray([0x01]), 1, "Index 1"),
            CharacteristicTestData(bytearray([0x7F]), 127, "Index 127"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Index 255"),
        ]
