"""Tests for FixedString8 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FixedString8Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestFixedString8Characteristic(CommonCharacteristicTests):
    """Test suite for FixedString8 characteristic."""

    @pytest.fixture
    def characteristic(self) -> FixedString8Characteristic:
        """Provide FixedString8 characteristic."""
        return FixedString8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for FixedString8."""
        return "2AF8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for FixedString8."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"12345678"),
                expected_value="12345678",
                description="full 8-char string",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"ABCDEFGH"),
                expected_value="ABCDEFGH",
                description="uppercase letters",
            ),
        ]
