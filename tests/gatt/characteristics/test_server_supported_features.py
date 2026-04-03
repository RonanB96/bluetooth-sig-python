"""Tests for Server Supported Features characteristic (0x2B3A)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.server_supported_features import (
    ServerFeatures,
    ServerSupportedFeaturesCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestServerSupportedFeatures(CommonCharacteristicTests):
    """Test suite for Server Supported Features characteristic."""

    @pytest.fixture
    def characteristic(self) -> ServerSupportedFeaturesCharacteristic:
        return ServerSupportedFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B3A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), ServerFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), ServerFeatures.EATT, "EATT supported"),
        ]

    def test_variable_length(self, characteristic: ServerSupportedFeaturesCharacteristic) -> None:
        """Test that multi-byte data is accepted."""
        result = characteristic.parse_value(bytearray([0x01, 0x00]))
        assert result == ServerFeatures.EATT
