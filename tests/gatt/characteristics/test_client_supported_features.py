"""Tests for Client Supported Features characteristic (0x2B29)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.client_supported_features import (
    ClientFeatures,
    ClientSupportedFeaturesCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestClientSupportedFeatures(CommonCharacteristicTests):
    """Test suite for Client Supported Features characteristic."""

    @pytest.fixture
    def characteristic(self) -> ClientSupportedFeaturesCharacteristic:
        return ClientSupportedFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B29"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), ClientFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), ClientFeatures.ROBUST_CACHING, "Robust caching"),
            CharacteristicTestData(bytearray([0x02]), ClientFeatures.EATT, "EATT"),
            CharacteristicTestData(
                bytearray([0x04]), ClientFeatures.MULTIPLE_HANDLE_VALUE_NOTIFICATIONS, "Multi notify"
            ),
            CharacteristicTestData(
                bytearray([0x07]),
                ClientFeatures.ROBUST_CACHING
                | ClientFeatures.EATT
                | ClientFeatures.MULTIPLE_HANDLE_VALUE_NOTIFICATIONS,
                "All features",
            ),
        ]

    def test_variable_length(self, characteristic: ClientSupportedFeaturesCharacteristic) -> None:
        """Test that multi-byte data is accepted."""
        result = characteristic.parse_value(bytearray([0x07, 0x00]))
        assert (
            result
            == ClientFeatures.ROBUST_CACHING | ClientFeatures.EATT | ClientFeatures.MULTIPLE_HANDLE_VALUE_NOTIFICATIONS
        )
