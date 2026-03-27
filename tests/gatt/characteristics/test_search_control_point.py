"""Tests for Search Control Point characteristic (0x2BA7)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.search_control_point import (
    SearchControlPointCharacteristic,
    SearchControlPointData,
    SearchControlPointType,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSearchControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Search Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> SearchControlPointCharacteristic:
        return SearchControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x08]),
                expected_value=SearchControlPointData(
                    length=2,
                    search_type=SearchControlPointType.ONLY_TRACKS,
                    parameter=None,
                ),
                description="Only Tracks search (no parameter string)",
            ),
            CharacteristicTestData(
                # Length=7, Type=Track Name(0x01), Parameter="Hello"
                input_data=bytearray([0x07, 0x01]) + bytearray(b"Hello"),
                expected_value=SearchControlPointData(
                    length=7,
                    search_type=SearchControlPointType.TRACK_NAME,
                    parameter="Hello",
                ),
                description="Track Name search with parameter 'Hello'",
            ),
            CharacteristicTestData(
                # Length=5, Type=Genre(0x07), Parameter="Pop"
                input_data=bytearray([0x05, 0x07]) + bytearray(b"Pop"),
                expected_value=SearchControlPointData(
                    length=5,
                    search_type=SearchControlPointType.GENRE,
                    parameter="Pop",
                ),
                description="Genre search with parameter 'Pop'",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = SearchControlPointCharacteristic()
        original = SearchControlPointData(
            length=8,
            search_type=SearchControlPointType.ARTIST_NAME,
            parameter="Bach",
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
