"""Tests for Central Address Resolution characteristic (0x2AA6)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.central_address_resolution import (
    CentralAddressResolutionCharacteristic,
    CentralAddressResolutionSupport,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCentralAddressResolution(CommonCharacteristicTests):
    """Test suite for Central Address Resolution characteristic."""

    @pytest.fixture
    def characteristic(self) -> CentralAddressResolutionCharacteristic:
        return CentralAddressResolutionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AA6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), CentralAddressResolutionSupport.NOT_SUPPORTED, "Not supported"),
            CharacteristicTestData(bytearray([0x01]), CentralAddressResolutionSupport.SUPPORTED, "Supported"),
        ]

    def test_roundtrip(self, characteristic: CentralAddressResolutionCharacteristic) -> None:
        for val in CentralAddressResolutionSupport:
            encoded = characteristic.build_value(val)
            assert characteristic.parse_value(encoded) == val
