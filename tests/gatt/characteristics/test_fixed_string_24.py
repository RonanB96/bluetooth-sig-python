"""Tests for FixedString24 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FixedString24Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestFixedString24Characteristic(CommonCharacteristicTests):
    """Test suite for FixedString24 characteristic."""

    @pytest.fixture
    def characteristic(self) -> FixedString24Characteristic:
        """Provide FixedString24 characteristic."""
        return FixedString24Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for FixedString24."""
        return "2AF6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for FixedString24."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"123456789012345678901234"),
                expected_value="123456789012345678901234",
                description="full 24-char string",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"ABCDEFGHIJKLMNOPQRSTUVWX"),
                expected_value="ABCDEFGHIJKLMNOPQRSTUVWX",
                description="uppercase letters",
            ),
        ]
