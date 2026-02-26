"""Tests for GenericLevel characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import GenericLevelCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestGenericLevelCharacteristic(CommonCharacteristicTests):
    """Test suite for GenericLevel characteristic."""

    @pytest.fixture
    def characteristic(self) -> GenericLevelCharacteristic:
        """Provide GenericLevel characteristic."""
        return GenericLevelCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for GenericLevel."""
        return "2AF9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for GenericLevel."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="zero level",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1000,
                description="level 1000",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]),
                expected_value=65535,
                description="max uint16",
            ),
        ]
