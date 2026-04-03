"""Tests for Chromaticity Coordinate characteristic (0x2B1C)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ChromaticityCoordinateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests

_RESOLUTION = 2**-16  # M=1, d=0, b=-16 → scale = 1/65536


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
                input_data=bytearray([0x00, 0x00]),
                expected_value=0.0,
                description="Minimum coordinate (raw 0, decoded 0.0)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x80]),
                expected_value=0x8000 * _RESOLUTION,
                description="Midpoint coordinate (raw 32768, decoded ~0.5)",
            ),
        ]

    def test_minimum_value(self) -> None:
        """Test minimum chromaticity coordinate."""
        char = ChromaticityCoordinateCharacteristic()
        result = char.parse_value(bytearray([0x00, 0x00]))
        assert result == pytest.approx(0.0)

    def test_midpoint_value(self) -> None:
        """Test midpoint chromaticity coordinate (~0.5)."""
        char = ChromaticityCoordinateCharacteristic()
        result = char.parse_value(bytearray([0x00, 0x80]))
        assert result == pytest.approx(0x8000 * _RESOLUTION)

    def test_near_maximum_value(self) -> None:
        """Test near-maximum chromaticity coordinate (~1.0)."""
        char = ChromaticityCoordinateCharacteristic()
        result = char.parse_value(bytearray([0xFF, 0xFF]))
        assert result == pytest.approx(65535 * _RESOLUTION, rel=1e-4)
