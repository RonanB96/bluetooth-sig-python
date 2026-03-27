"""Tests for BGSFeaturesCharacteristic (2C03)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bgs_features import BGSFeatures, BGSFeaturesCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBGSFeatures(CommonCharacteristicTests):
    """Test suite for BGSFeaturesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BGSFeaturesCharacteristic:
        return BGSFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C03"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), BGSFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), BGSFeatures.MULTISINK, "Multisink"),
            CharacteristicTestData(bytearray([0x03]), BGSFeatures.MULTISINK | BGSFeatures.MULTIPLEX, "All features"),
        ]

    def test_roundtrip(self, characteristic: BGSFeaturesCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), BGSFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), BGSFeatures.MULTISINK, "Multisink"),
            CharacteristicTestData(bytearray([0x03]), BGSFeatures.MULTISINK | BGSFeatures.MULTIPLEX, "All features"),
        ]
