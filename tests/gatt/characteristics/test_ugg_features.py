"""Tests for UGGFeaturesCharacteristic (2C01)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ugg_features import UGGFeatures, UGGFeaturesCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUGGFeatures(CommonCharacteristicTests):
    """Test suite for UGGFeaturesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> UGGFeaturesCharacteristic:
        return UGGFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C01"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), UGGFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), UGGFeatures.UGG_MULTIPLEX, "Multiplex"),
            CharacteristicTestData(
                bytearray([0x07]),
                UGGFeatures.UGG_MULTIPLEX | UGGFeatures.UGG_96_KBPS | UGGFeatures.UGG_MULTISINK,
                "All features",
            ),
        ]
