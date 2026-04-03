"""Tests for URICharacteristic (2AB6)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.uri import URICharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestURI(CommonCharacteristicTests):
    """Test suite for URICharacteristic."""

    @pytest.fixture
    def characteristic(self) -> URICharacteristic:
        return URICharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AB6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"https://example.com"), "https://example.com", "HTTPS URI"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
