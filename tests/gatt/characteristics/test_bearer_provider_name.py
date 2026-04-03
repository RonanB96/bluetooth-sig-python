"""Tests for BearerProviderNameCharacteristic (2BB3)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_provider_name import BearerProviderNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBearerProviderName(CommonCharacteristicTests):
    """Test suite for BearerProviderNameCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BearerProviderNameCharacteristic:
        return BearerProviderNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Vodafone"), "Vodafone", "Vodafone"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
