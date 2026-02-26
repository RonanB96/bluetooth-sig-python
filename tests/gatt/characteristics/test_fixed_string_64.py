"""Tests for FixedString64 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FixedString64Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestFixedString64Characteristic(CommonCharacteristicTests):
    """Test suite for FixedString64 characteristic."""

    @pytest.fixture
    def characteristic(self) -> FixedString64Characteristic:
        """Provide FixedString64 characteristic."""
        return FixedString64Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for FixedString64."""
        return "2BDE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for FixedString64."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"A" * 64),
                expected_value="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                description="64 A's",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"1234567890" * 6 + b"1234"),
                expected_value="1234567890" * 6 + "1234",
                description="repeating digits",
            ),
        ]
