"""Tests for FixedString36 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FixedString36Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestFixedString36Characteristic(CommonCharacteristicTests):
    """Test suite for FixedString36 characteristic."""

    @pytest.fixture
    def characteristic(self) -> FixedString36Characteristic:
        """Provide FixedString36 characteristic."""
        return FixedString36Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for FixedString36."""
        return "2AF7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for FixedString36."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"123456789012345678901234567890123456"),
                expected_value="123456789012345678901234567890123456",
                description="full 36-char string",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
                expected_value="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                description="alphanumeric",
            ),
        ]
