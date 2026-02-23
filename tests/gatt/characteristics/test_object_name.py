"""Tests for Object Name characteristic (0x2ABE)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ObjectNameCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectNameCharacteristic(CommonCharacteristicTests):
    """Test suite for Object Name characteristic."""

    @pytest.fixture
    def characteristic(self) -> ObjectNameCharacteristic:
        return ObjectNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ABE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"hello"),
                expected_value="hello",
                description="Simple ASCII name",
            ),
            CharacteristicTestData(
                input_data=bytearray(b""),
                expected_value="",
                description="Empty name",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = ObjectNameCharacteristic()
        original = "My Photo.jpg"
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_utf8_round_trip(self) -> None:
        """Verify UTF-8 encoding round-trip."""
        char = ObjectNameCharacteristic()
        original = "caf\u00e9"
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
