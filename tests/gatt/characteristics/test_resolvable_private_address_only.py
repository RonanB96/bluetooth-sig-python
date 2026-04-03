"""Tests for Resolvable Private Address Only characteristic (0x2AC9).

BT Core Spec v6.0, Vol 3, Part C, Section 12.5:
  1 octet uint8.  Value 0 = only RPAs used after bonding.
  All other values reserved for future use.
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.resolvable_private_address_only import (
    ResolvablePrivateAddressOnlyCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestResolvablePrivateAddressOnly(CommonCharacteristicTests):
    """Test suite for Resolvable Private Address Only characteristic."""

    @pytest.fixture
    def characteristic(self) -> ResolvablePrivateAddressOnlyCharacteristic:
        return ResolvablePrivateAddressOnlyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "RPA only (defined value)"),
            CharacteristicTestData(bytearray([0xFF]), 0xFF, "Reserved value 0xFF"),
        ]
