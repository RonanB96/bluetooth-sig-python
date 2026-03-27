"""Tests for BearerTechnologyCharacteristic (2BB5)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_technology import BearerTechnology, BearerTechnologyCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBearerTechnology(CommonCharacteristicTests):
    """Test suite for BearerTechnologyCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BearerTechnologyCharacteristic:
        return BearerTechnologyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), BearerTechnology.THREEG, "3G"),
            CharacteristicTestData(bytearray([0x02]), BearerTechnology.FOURGEE, "4G"),
            CharacteristicTestData(bytearray([0x03]), BearerTechnology.LTE, "LTE"),
            CharacteristicTestData(bytearray([0x04]), BearerTechnology.WIFI, "Wi-Fi"),
            CharacteristicTestData(bytearray([0x05]), BearerTechnology.FIVEG, "5G"),
        ]

    def test_roundtrip(self, characteristic: BearerTechnologyCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), BearerTechnology.THREEG, "3G"),
            CharacteristicTestData(bytearray([0x02]), BearerTechnology.FOURGEE, "4G"),
            CharacteristicTestData(bytearray([0x03]), BearerTechnology.LTE, "LTE"),
            CharacteristicTestData(bytearray([0x04]), BearerTechnology.WIFI, "Wi-Fi"),
            CharacteristicTestData(bytearray([0x05]), BearerTechnology.FIVEG, "5G"),
        ]
