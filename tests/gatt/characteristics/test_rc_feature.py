"""Tests for RCFeatureCharacteristic (2B1D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.rc_feature import RCFeature, RCFeatureCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRCFeature(CommonCharacteristicTests):
    """Test suite for RCFeatureCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> RCFeatureCharacteristic:
        return RCFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B1D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00]), RCFeature(0), "No features"),
            CharacteristicTestData(bytearray([0x01, 0x00]), RCFeature.E2E_CRC_SUPPORT, "CRC support"),
            CharacteristicTestData(
                bytearray([0x03, 0x00]),
                RCFeature.E2E_CRC_SUPPORT | RCFeature.RECONNECTION_TIMEOUT_SUPPORT,
                "All features",
            ),
        ]

    def test_roundtrip(self, characteristic: RCFeatureCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00]), RCFeature(0), "No features"),
            CharacteristicTestData(bytearray([0x01, 0x00]), RCFeature.E2E_CRC_SUPPORT, "CRC support"),
            CharacteristicTestData(
                bytearray([0x03, 0x00]),
                RCFeature.E2E_CRC_SUPPORT | RCFeature.RECONNECTION_TIMEOUT_SUPPORT,
                "All features",
            ),
        ]
