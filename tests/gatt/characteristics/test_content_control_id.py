"""Tests for ContentControlId characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ContentControlIdCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestContentControlIdCharacteristic(CommonCharacteristicTests):
    """Test suite for ContentControlId characteristic."""

    @pytest.fixture
    def characteristic(self) -> ContentControlIdCharacteristic:
        """Provide ContentControlId characteristic."""
        return ContentControlIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ContentControlId."""
        return "2BBA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for ContentControlId."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0]),
                expected_value=0,
                description="zero ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([42]),
                expected_value=42,
                description="ID 42",
            ),
            CharacteristicTestData(
                input_data=bytearray([255]),
                expected_value=255,
                description="max uint8",
            ),
        ]
