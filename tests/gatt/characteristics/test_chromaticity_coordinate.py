"""Tests for Chromaticity Coordinate characteristic (0x2B1C)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ChromaticityCoordinateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestChromaticityCoordinateCharacteristic(CommonCharacteristicTests):
    """Test suite for Chromaticity Coordinate characteristic."""

    @pytest.fixture
    def characteristic(self) -> ChromaticityCoordinateCharacteristic:
        """Return a Chromaticity Coordinate characteristic instance."""
        return ChromaticityCoordinateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Chromaticity Coordinate characteristic."""
        return "2B1C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for chromaticity coordinate."""
        return [
            CharacteristicTestData(
                input_data=bytearray([16, 0]), expected_value=0, description="Minimum coordinate (raw 16, decoded 0)"
            ),
            CharacteristicTestData(
                input_data=bytearray([17, 0]), expected_value=1, description="Near minimum (raw 17, decoded 1)"
            ),
        ]

    def test_minimum_value(self) -> None:
        """Test minimum chromaticity coordinate."""
        char = ChromaticityCoordinateCharacteristic()
        result = char.decode_value(bytearray([16, 0]))
        assert result == 0

    def test_maximum_value(self) -> None:
        """Test near minimum chromaticity coordinate."""
        char = ChromaticityCoordinateCharacteristic()
        result = char.decode_value(bytearray([17, 0]))
        assert result == 1

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = ChromaticityCoordinateCharacteristic()
        # Scaling: value = raw - 16, so integer values round-trip exactly
        for value in [0, 1, 100, 1000, 65535 - 16]:
            encoded = char.encode_value(value)
            decoded = char.decode_value(encoded)
            assert decoded == value, f"Round trip failed for {value}: got {decoded}"
