"""Tests for FixedString16 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FixedString16Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestFixedString16Characteristic(CommonCharacteristicTests):
    """Test suite for FixedString16 characteristic."""

    @pytest.fixture
    def characteristic(self) -> FixedString16Characteristic:
        """Provide FixedString16 characteristic."""
        return FixedString16Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for FixedString16."""
        return "2AF5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for FixedString16."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"1234567890123456"),
                expected_value="1234567890123456",
                description="full 16-char string",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"ABCDEFGHIJKLMNOP"),
                expected_value="ABCDEFGHIJKLMNOP",
                description="uppercase letters",
            ),
        ]
