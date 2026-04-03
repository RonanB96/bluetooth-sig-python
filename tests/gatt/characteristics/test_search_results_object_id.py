"""Tests for Search Results Object ID characteristic (0x2BA6)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.search_results_object_id import (
    SearchResultsObjectIdCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSearchResultsObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Search Results Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> SearchResultsObjectIdCharacteristic:
        return SearchResultsObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x15, 0xCD, 0x5B, 0x07, 0x00, 0x00]),
                expected_value=123456789,
                description="Object ID = 123456789",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]
