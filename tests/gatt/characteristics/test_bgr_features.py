"""Tests for BGRFeaturesCharacteristic (2C04)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bgr_features import BGRFeatures, BGRFeaturesCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBGRFeatures(CommonCharacteristicTests):
    """Test suite for BGRFeaturesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BGRFeaturesCharacteristic:
        return BGRFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C04"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), BGRFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), BGRFeatures.MULTISINK, "Multisink"),
            CharacteristicTestData(bytearray([0x03]), BGRFeatures.MULTISINK | BGRFeatures.MULTIPLEX, "All features"),
        ]
