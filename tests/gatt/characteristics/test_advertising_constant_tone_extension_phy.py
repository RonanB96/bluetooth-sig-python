"""Tests for AdvertisingConstantToneExtensionPhyCharacteristic (2BB2)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.advertising_constant_tone_extension_phy import (
    CTEPHY,
    AdvertisingConstantToneExtensionPhyCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAdvertisingConstantToneExtensionPhy(CommonCharacteristicTests):
    """Test suite for AdvertisingConstantToneExtensionPhyCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AdvertisingConstantToneExtensionPhyCharacteristic:
        return AdvertisingConstantToneExtensionPhyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), CTEPHY.LE_1M, "LE 1M PHY"),
            CharacteristicTestData(bytearray([0x01]), CTEPHY.LE_2M, "LE 2M PHY"),
        ]
