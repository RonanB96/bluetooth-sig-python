"""Tests for UGTFeaturesCharacteristic (2C02)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ugt_features import UGTFeatures, UGTFeaturesCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUGTFeatures(CommonCharacteristicTests):
    """Test suite for UGTFeaturesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> UGTFeaturesCharacteristic:
        return UGTFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C02"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), UGTFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), UGTFeatures.UGT_SOURCE, "Source"),
            CharacteristicTestData(
                bytearray([0x7F]),
                UGTFeatures.UGT_SOURCE
                | UGTFeatures.UGT_80_KBPS_SOURCE
                | UGTFeatures.UGT_SINK
                | UGTFeatures.UGT_64_KBPS_SINK
                | UGTFeatures.UGT_MULTIPLEX
                | UGTFeatures.UGT_MULTISINK
                | UGTFeatures.UGT_MULTISOURCE,
                "All features",
            ),
        ]
