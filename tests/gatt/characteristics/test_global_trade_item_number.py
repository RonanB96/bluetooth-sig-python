"""Tests for GlobalTradeItemNumber characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import GlobalTradeItemNumberCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestGlobalTradeItemNumberCharacteristic(CommonCharacteristicTests):
    """Test suite for GlobalTradeItemNumber characteristic."""

    @pytest.fixture
    def characteristic(self) -> GlobalTradeItemNumberCharacteristic:
        """Provide GlobalTradeItemNumber characteristic."""
        return GlobalTradeItemNumberCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for GlobalTradeItemNumber."""
        return "2AFA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for GlobalTradeItemNumber."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06]),
                expected_value=6618611909121,
                description="GTIN value",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=1,
                description="GTIN = 1",
            ),
        ]
