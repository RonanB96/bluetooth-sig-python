"""Tests for HTTPS Security characteristic (0x2ABB)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.https_security import (
    HttpsSecurityCharacteristic,
    HttpsSecurityState,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHttpsSecurity(CommonCharacteristicTests):
    """Test suite for HTTPS Security characteristic."""

    @pytest.fixture
    def characteristic(self) -> HttpsSecurityCharacteristic:
        return HttpsSecurityCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ABB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), HttpsSecurityState.HTTP, "HTTP"),
            CharacteristicTestData(bytearray([0x01]), HttpsSecurityState.HTTPS, "HTTPS"),
        ]

    def test_roundtrip(self, characteristic: HttpsSecurityCharacteristic) -> None:
        for val in HttpsSecurityState:
            encoded = characteristic.build_value(val)
            assert characteristic.parse_value(encoded) == val
