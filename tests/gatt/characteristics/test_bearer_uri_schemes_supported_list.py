"""Tests for BearerURISchemesCharacteristic (2BB6)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_uri_schemes_supported_list import BearerURISchemesCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBearerURISchemes(CommonCharacteristicTests):
    """Test suite for BearerURISchemesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BearerURISchemesCharacteristic:
        return BearerURISchemesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"tel,skype"), "tel,skype", "Tel and Skype"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]

    def test_roundtrip(self, characteristic: BearerURISchemesCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"tel,skype"), "tel,skype", "Tel and Skype"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
